function networkDiagnostics() {
    return {
        isAnalyzing: false,
        results: null,
        progress: 0,
        progressMessage: 'Initializing...',
        
        // Result data
        healthScore: 0,
        downloadSpeed: 0,
        uploadSpeed: 0,
        averageLatency: 0,
        jitter: 0,
        dnsLatency: 0,
        fastestDNS: '',
        packetLoss: 0,
        packetsLost: 0,
        packetsSent: 0,
        diagnosis: '',
        explanation: '',
        recommendation: '',
        metricsSummary: {},
        
        apiUrl: 'http://localhost:8000', //local
        // apiUrl: window.location.origin,  //deployment
        
        async init() {
            this.checkAPIConnection();
            const path = window.location.pathname;
            if (path.startsWith("/report/")) {
                const response = await fetch(`${this.apiUrl}${path}`);
                if (response.ok) {
                    const data = await response.json();
                    this.processResults(data);
                    this.results = data;
                }
            }
        },
        
        async checkAPIConnection() {
            try {
                const response = await fetch(`${this.apiUrl}/health`);
                if (!response.ok) {
                    console.error('API health check failed');
                }
            } catch (error) {
                console.error('Cannot connect to API:', error);
                this.apiUrl = window.location.hostname === 'localhost' 
                    ? 'http://localhost:8000' 
                    : `${window.location.protocol}//${window.location.hostname}:8000`;
            }
        },
        
        async startAnalysis() {
            this.isAnalyzing = true;
            this.results = null;
            this.progress = 0;
            
            // Simulate progress updates
            this.simulateProgress();
            
            try {
                const response = await fetch(`${this.apiUrl}/diagnostics/full-analysis`);
                
                if (!response.ok) {
                    throw new Error('Analysis failed');
                }
                
                const data = await response.json();
                this.processResults(data);
                
            } catch (error) {
                console.error('Analysis error:', error);
                this.showError(error.message);
            } finally {
                this.isAnalyzing = false;
                this.progress = 100;
            }
        },

        async shareReport() {
            if (!this.results) return;
            const response = await fetch(`${this.apiUrl}/diagnostics/share`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(this.results)
            });
            const data = await response.json();
            const url = `${window.location.origin}${data.share_url}`;

            navigator.clipboard.writeText(url);
            alert("Share link copied to clipboard!\n\n" + url);
        },
        
        simulateProgress() {
            const messages = [
                'Testing network speed...',
                'Measuring latency...',
                'Checking DNS performance...',
                'Hang on, this may take 15-30 seconds',
                'Analyzing packet loss...',
                'Processing results...'
            ];
            
            let currentMessage = 0;
            const interval = setInterval(() => {
                if (!this.isAnalyzing) {
                    clearInterval(interval);
                    return;
                }
                
                this.progress = Math.min(this.progress + 15, 90);
                this.progressMessage = messages[currentMessage % messages.length];
                currentMessage++;
                
            }, 2000);
        },
        
        processResults(data) {
            this.results = data;
            
            // Extract analysis results
            const analysis = data.analysis || {};
            this.healthScore = analysis.health_score || 0;
            this.diagnosis = analysis.diagnosis || 'Analysis Complete';
            this.explanation = analysis.explanation || 'No issues detected.';
            this.recommendation = analysis.recommendation || 'Your connection appears healthy.';
            this.metricsSummary = analysis.metrics_summary || {};
            
            // Extract speed metrics
            const speed = data.speed || {};
            this.downloadSpeed = speed.download_mbps || 0;
            this.uploadSpeed = speed.upload_mbps || 0;
            
            // Extract latency metrics
            const latency = data.latency || {};
            this.averageLatency = latency.summary?.average || 0;
            this.jitter = latency.summary?.jitter || 0;
            
            // Extract DNS metrics
            const dns = data.dns || {};
            this.dnsLatency = dns.summary?.average || 0;
            const fastest = dns.summary?.fastest_server || "";
            
            const dnsNames = {
                "1.1.1.1": "Cloudflare",
                "8.8.8.8": "Google",
                "8.8.4.4": "Google",
                "9.9.9.9": "Quad9"
            };

            this.fastestDNS = fastest
                ? `${dnsNames[fastest] || "DNS"} (${fastest})`
                : "";
            
            // Extract packet loss metrics
            const packetLoss = data.packet_loss || {};
            this.packetLoss = packetLoss.packet_loss_percent || 0;
            this.packetsLost = packetLoss.packets_lost || 0;
            this.packetsSent = packetLoss.packets_sent || 0;
            
            // Draw health gauge
            this.$nextTick(() => {
                this.drawHealthGauge();
            });
        },

        drawHealthGauge() {
            const canvas = document.getElementById('healthGauge');
            if (!canvas) return;

            const ctx = canvas.getContext('2d');

            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const radius = 90;

            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw background arc
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, Math.PI * 0.75, Math.PI * 2.25, false);
            ctx.lineWidth = 20;
            ctx.strokeStyle = '#334155';
            ctx.stroke();

            // Draw score arc
            const scoreAngle = (this.healthScore / 100) * Math.PI * 1.5;

            ctx.beginPath();
            ctx.arc(
                centerX,
                centerY,
                radius,
                Math.PI * 0.75,
                Math.PI * 0.75 + scoreAngle,
                false
            );

            ctx.lineWidth = 20;

            const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);

            if (this.healthScore >= 80) {
                gradient.addColorStop(0, '#10b981');
                gradient.addColorStop(1, '#34d399');
            }
            else if (this.healthScore >= 50) {
                gradient.addColorStop(0, '#f59e0b');
                gradient.addColorStop(1, '#fbbf24');
            }
            else {
                gradient.addColorStop(0, '#ef4444');
                gradient.addColorStop(1, '#f87171');
            }

            ctx.strokeStyle = gradient;
            ctx.lineCap = 'round';
            ctx.stroke();
        },
        
        getScoreColor() {
            if (this.healthScore >= 80) return 'text-green-400';
            if (this.healthScore >= 50) return 'text-yellow-400';
            return 'text-red-400';
        },
        
        getScoreLabel() {
            if (this.healthScore >= 80) return 'Excellent';
            if (this.healthScore >= 60) return 'Good';
            if (this.healthScore >= 40) return 'Fair';
            return 'Poor';
        },
        
        getMetricBadgeClass(metric) {
            const status = this.metricsSummary[metric] || 'unknown';
            const classes = {
                'excellent': 'bg-green-900 text-green-300',
                'good': 'bg-blue-900 text-blue-300',
                'fair': 'bg-yellow-900 text-yellow-300',
                'poor': 'bg-red-900 text-red-300',
                'unknown': 'bg-slate-700 text-slate-400'
            };
            return classes[status] || classes['unknown'];
        },
        
        getMetricLabel(metric) {
            const status = this.metricsSummary[metric] || 'unknown';
            return status.charAt(0).toUpperCase() + status.slice(1);
        },
        
        formatSpeed(value) {
            return value ? value.toFixed(1) : '—';
        },
        
        formatLatency(value) {
            return value ? Math.round(value) : '—';
        },
        
        formatPacketLoss(value) {
            return value !== null && value !== undefined ? value.toFixed(1) : '—';
        },
        
        async exportResults() {
            if (!this.results) return;
            const response = await fetch(`${this.apiUrl}/diagnostics/export-pdf`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(this.results)
            });

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = "fixmyinternet-report.pdf";
            a.click();

            window.URL.revokeObjectURL(url);
        },
        
        showError(message) {
            this.results = {
                analysis: {
                    health_score: 0,
                    diagnosis: '❌ Analysis Failed',
                    explanation: message || 'Unable to complete network analysis.',
                    recommendation: 'Please check your connection and try again.'
                }
            };
        }
    };
}
