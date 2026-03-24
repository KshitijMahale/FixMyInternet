const API_BASE = window.location.origin;

const state = {
  chart: null,
  progressTimer: null,
  stagedMessages: [
    "Testing Speed...",
    "Testing Latency...",
    "Testing DNS...",
    "Checking Packet Loss...",
    "Analyzing Connection..."
  ],
};

const elements = {
  analyzeBtn: document.getElementById("analyzeBtn"),
  progressPanel: document.getElementById("progressPanel"),
  progressBar: document.getElementById("progressBar"),
  progressPct: document.getElementById("progressPct"),
  progressMessage: document.getElementById("progressMessage"),
  resultsSection: document.getElementById("resultsSection"),
  healthScore: document.getElementById("healthScore"),
  healthGrade: document.getElementById("healthGrade"),
  diagnosis: document.getElementById("diagnosis"),
  explanation: document.getElementById("explanation"),
  recommendation: document.getElementById("recommendation"),
  downloadSpeed: document.getElementById("downloadSpeed"),
  uploadSpeed: document.getElementById("uploadSpeed"),
  latencyAvg: document.getElementById("latencyAvg"),
  latencyJitter: document.getElementById("latencyJitter"),
  dnsAvg: document.getElementById("dnsAvg"),
  dnsFastest: document.getElementById("dnsFastest"),
  packetLoss: document.getElementById("packetLoss"),
  packetLossCounts: document.getElementById("packetLossCounts"),
};

function scoreColor(score) {
  if (score >= 80) return "#22c55e";
  if (score >= 50) return "#f59e0b";
  return "#ef4444";
}

function scoreLabel(score) {
  if (score >= 80) return "Healthy";
  if (score >= 50) return "Degraded";
  return "Unstable";
}

function numberOrDash(value, digits = 1) {
  if (typeof value !== "number" || Number.isNaN(value)) return "-";
  return value.toFixed(digits);
}

function startProgressSimulation() {
  elements.progressPanel.classList.remove("hidden");
  elements.resultsSection.classList.add("hidden");

  let progress = 0;
  let messageIndex = 0;

  elements.progressMessage.textContent = state.stagedMessages[messageIndex];

  state.progressTimer = setInterval(() => {
    progress = Math.min(progress + 8, 92);
    if (progress % 20 === 0 && messageIndex < state.stagedMessages.length - 1) {
      messageIndex += 1;
      elements.progressMessage.textContent = state.stagedMessages[messageIndex];
    }

    elements.progressBar.style.width = `${progress}%`;
    elements.progressPct.textContent = `${progress}%`;
  }, 500);
}

function completeProgress() {
  if (state.progressTimer) {
    clearInterval(state.progressTimer);
    state.progressTimer = null;
  }
  elements.progressBar.style.width = "100%";
  elements.progressPct.textContent = "100%";
  elements.progressMessage.textContent = "Done";
}

function renderGauge(score) {
  const canvas = document.getElementById("healthGauge");
  const ctx = canvas.getContext("2d");

  if (state.chart) {
    state.chart.destroy();
  }

  state.chart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Health", "Remaining"],
      datasets: [
        {
          data: [score, 100 - score],
          backgroundColor: [scoreColor(score), "#334155"],
          borderWidth: 0,
          cutout: "78%",
          circumference: 280,
          rotation: 220,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
      },
    },
  });
}

function renderResults(data) {
  const speed = data.speed || {};
  const latencySummary = (data.latency || {}).summary || {};
  const dnsSummary = (data.dns || {}).summary || {};
  const packetLoss = data.packet_loss || {};
  const analysis = data.analysis || {};

  const healthScore = Number(analysis.health_score || 0);
  const latencyMin = latencySummary.minimum_latency_ms;
  const latencyMax = latencySummary.maximum_latency_ms;
  const jitter =
    typeof latencyMin === "number" && typeof latencyMax === "number"
      ? latencyMax - latencyMin
      : null;

  elements.healthScore.textContent = `${healthScore}`;
  elements.healthGrade.textContent = scoreLabel(healthScore);
  elements.diagnosis.textContent = analysis.diagnosis || "No diagnosis available";
  elements.explanation.textContent = analysis.explanation || "No explanation available";
  elements.recommendation.textContent = analysis.recommendation || "No recommendation available";

  elements.downloadSpeed.textContent = numberOrDash(speed.download_mbps, 2);
  elements.uploadSpeed.textContent = numberOrDash(speed.upload_mbps, 2);
  elements.latencyAvg.textContent = numberOrDash(latencySummary.average_latency_ms, 2);
  elements.latencyJitter.textContent = numberOrDash(jitter, 2);
  elements.dnsAvg.textContent = numberOrDash(dnsSummary.average_latency_ms, 2);
  elements.dnsFastest.textContent = `Fastest: ${dnsSummary.fastest_server || "-"}`;
  elements.packetLoss.textContent = numberOrDash(packetLoss.packet_loss_percent, 2);
  elements.packetLossCounts.textContent = `${packetLoss.packets_lost ?? "-"} lost of ${packetLoss.packets_sent ?? "-"}`;

  renderGauge(healthScore);
  elements.resultsSection.classList.remove("hidden");
}

async function runDiagnostics() {
  elements.analyzeBtn.disabled = true;
  elements.analyzeBtn.textContent = "Running...";
  startProgressSimulation();

  try {
    const response = await fetch(`${API_BASE}/diagnostics/full-analysis`);
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    completeProgress();
    renderResults(data);
  } catch (error) {
    completeProgress();
    elements.resultsSection.classList.remove("hidden");
    elements.diagnosis.textContent = "Analysis failed";
    elements.explanation.textContent = "Unable to complete diagnostics right now.";
    elements.recommendation.textContent = "Check backend logs and try again.";
  } finally {
    elements.analyzeBtn.disabled = false;
    elements.analyzeBtn.textContent = "Analyze My Internet";
  }
}

elements.analyzeBtn.addEventListener("click", runDiagnostics);
