from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class RootCauseAnalyzer:
    def __init__(self):
        self.thresholds = {
            'latency': {
                'excellent': 20,
                'good': 50,
                'fair': 80,
                'poor': 150
            },
            'dns': {
                'excellent': 30,
                'good': 60,
                'fair': 100,
                'poor': 200
            },
            'packet_loss': {
                'excellent': 0,
                'good': 1,
                'fair': 2,
                'poor': 5
            },
            'speed': {
                'excellent': 100,
                'good': 25,
                'fair': 10,
                'poor': 5
            }
        }
    
    def analyze(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform root cause analysis on test results"""
        
        latency_avg = test_results.get('latency', {}).get('summary', {}).get('average')
        latency_jitter = test_results.get('latency', {}).get('summary', {}).get('jitter')
        dns_avg = test_results.get('dns', {}).get('summary', {}).get('average')
        packet_loss = test_results.get('packet_loss', {}).get('packet_loss_percent')
        download_speed = test_results.get('speed', {}).get('download_mbps')
        upload_speed = test_results.get('speed', {}).get('upload_mbps')
        
        health_score = self._calculate_health_score(
            latency_avg, dns_avg, packet_loss, download_speed
        )
        
        diagnosis, explanation, recommendation = self._get_diagnosis(
            latency_avg, latency_jitter, dns_avg, packet_loss, 
            download_speed, upload_speed
        )
        
        status = self._get_status(health_score)
        
        return {
            'health_score': health_score,
            'status': status,
            'diagnosis': diagnosis,
            'explanation': explanation,
            'recommendation': recommendation,
            'metrics_summary': {
                'latency': self._categorize_metric(latency_avg, 'latency'),
                'dns': self._categorize_metric(dns_avg, 'dns'),
                'packet_loss': self._categorize_metric(packet_loss, 'packet_loss'),
                'speed': self._categorize_metric(download_speed, 'speed')
            }
        }
    
    def _calculate_health_score(self, latency: Optional[float], dns: Optional[float], 
                                packet_loss: Optional[float], speed: Optional[float]) -> int:
        """Calculate overall health score (0-100)"""
        score = 100
        
        if latency is not None:
            if latency > 150:
                score -= 30
            elif latency > 80:
                score -= 15
            elif latency > 50:
                score -= 5
        else:
            score -= 20  
        
        if dns is not None:
            if dns > 200:
                score -= 25
            elif dns > 100:
                score -= 15
            elif dns > 60:
                score -= 5
        else:
            score -= 15
        
        if packet_loss is not None:
            if packet_loss > 10:
                score -= 40
            elif packet_loss > 5:
                score -= 25
            elif packet_loss > 2:
                score -= 10
        else:
            score -= 20
        
        if speed is not None:
            if speed < 5:
                score -= 30
            elif speed < 10:
                score -= 20
            elif speed < 25:
                score -= 10
        else:
            score -= 15
        
        return max(0, min(100, score))
    
    def _get_diagnosis(self, latency: Optional[float], jitter: Optional[float],
                       dns: Optional[float], packet_loss: Optional[float],
                       download: Optional[float], upload: Optional[float]) -> Tuple[str, str, str]:
        """Determine the primary issue and recommendation"""
        
        issues = []
        
        # Check for critical issues first
        if packet_loss and packet_loss > 5:
            return (
                "High Packet Loss Detected",
                f"Your connection is dropping {packet_loss}% of data packets. This causes interruptions in streaming, gaming, and video calls.",
                "Try connecting via Ethernet cable instead of WiFi. If already wired, contact your ISP as this may indicate a line issue."
            )
        
        if latency and latency > 120:
            if jitter and jitter > 80:
                return (
                    "Unstable WiFi Connection",
                    f"High latency ({latency:.0f}ms) with significant jitter ({jitter:.0f}ms) indicates WiFi interference or weak signal.",
                    "Move closer to your router, switch to 5GHz band, or use an Ethernet cable for stable connection."
                )
            else:
                return (
                    "High Network Latency",
                    f"Latency of {latency:.0f}ms will cause noticeable delays in gaming and video calls.",
                    "Check if other devices are using bandwidth. Consider upgrading your internet plan or switching ISPs."
                )
        
        if dns and dns > 120:
            return (
                "Slow DNS Server",
                f"DNS resolution taking {dns:.0f}ms is slowing down website loading.",
                "Switch to faster DNS servers: Cloudflare (1.1.1.1) or Google (8.8.8.8) in your network settings."
            )
        
        if download and download < 5:
            return (
                "Very Low Internet Speed",
                f"Download speed of {download:.1f} Mbps is insufficient for modern internet use.",
                "Restart your router, check for service outages, or contact your ISP to upgrade your plan."
            )
        
        if packet_loss and packet_loss > 2:
            return (
                "Minor Packet Loss",
                f"Experiencing {packet_loss}% packet loss which may cause occasional stuttering.",
                "Check cable connections and restart your router. Monitor if the issue persists."
            )
        
        if latency and latency > 80 and packet_loss and packet_loss < 1:
            return (
                "ISP Network Congestion",
                "High latency without packet loss typically indicates ISP network congestion.",
                "Test at different times of day. Consider contacting your ISP about congestion issues."
            )
        
        if download and download < 25:
            return (
                "Below Average Speed",
                f"Speed of {download:.1f} Mbps may struggle with multiple devices or 4K streaming.",
                "Close unnecessary applications, check for WiFi interference, or upgrade your internet plan."
            )
        
        return (
            "Connection Healthy",
            "Your internet connection is performing well with no significant issues detected.",
            "Continue monitoring periodically to ensure consistent performance."
        )
    
    def _categorize_metric(self, value: Optional[float], metric_type: str) -> str:
        """Categorize a metric as excellent/good/fair/poor"""
        if value is None:
            return "unknown"
        
        thresholds = self.thresholds[metric_type]
        
        if metric_type == 'packet_loss':
            if value <= thresholds['excellent']:
                return "excellent"
            elif value <= thresholds['good']:
                return "good"
            elif value <= thresholds['fair']:
                return "fair"
            else:
                return "poor"
        elif metric_type == 'speed':
            if value >= thresholds['excellent']:
                return "excellent"
            elif value >= thresholds['good']:
                return "good"
            elif value >= thresholds['fair']:
                return "fair"
            else:
                return "poor"
        else:  # latency, dns (lower is better)
            if value <= thresholds['excellent']:
                return "excellent"
            elif value <= thresholds['good']:
                return "good"
            elif value <= thresholds['fair']:
                return "fair"
            else:
                return "poor"
    
    def _get_status(self, health_score: int) -> str:
        """Get status based on health score"""
        if health_score >= 80:
            return "excellent"
        elif health_score >= 60:
            return "good"
        elif health_score >= 40:
            return "fair"
        else:
            return "poor"
