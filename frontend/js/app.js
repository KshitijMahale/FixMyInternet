const API_BASE = window.location.origin;

const state = {
  chart: null,
  progressTimer: null,
  progressStepIndex: 0,
  connectionInfo: {
    isp: null,
    city: null,
    ip: null,
    server: null,
  },
  stagedMessages: [
    "Testing Speed...",
    "Testing Latency...",
    "Testing DNS...",
    "Checking Packet Loss...",
    "Analyzing Connection..."
  ],
  stepDurations: [1500, 2000, 1200, 1800, 1000]
};

const REQUIRED_ELEMENT_KEYS = [
  "analyzeBtn",
  "progressPanel",
  "progressMessage",
  "resultsSection",
  "connectionSummary",
  "healthChecklist",
  "healthScore",
  "healthGrade",
  "diagnosis",
  "explanation",
  "recommendation",
  "suggestionList",
];

const elements = {
  analyzeBtn: document.getElementById("analyzeBtn"),
  progressPanel: document.getElementById("progressPanel"),
  progressSteps: document.querySelectorAll("#progressSteps li"),
  progressMessage: document.getElementById("progressMessage"),
  resultsSection: document.getElementById("resultsSection"),
  connectionSummary: document.getElementById("connectionSummary"),
  healthChecklist: document.getElementById("healthChecklist"),
  healthScore: document.getElementById("healthScore"),
  healthGrade: document.getElementById("healthGrade"),
  diagnosis: document.getElementById("diagnosis"),
  explanation: document.getElementById("explanation"),
  recommendation: document.getElementById("recommendation"),
  suggestionList: document.getElementById("suggestionList"),
  downloadSpeed: document.getElementById("downloadSpeed"),
  uploadSpeed: document.getElementById("uploadSpeed"),
  speedRating: document.getElementById("speedRating"),
  speedMeaning: document.getElementById("speedMeaning"),
  downloadLabel: document.getElementById("downloadLabel"),
  uploadLabel: document.getElementById("uploadLabel"),
  latencyAvg: document.getElementById("latencyAvg"),
  latencyBest: document.getElementById("latencyBest"),
  latencyWorst: document.getElementById("latencyWorst"),
  latencyRating: document.getElementById("latencyRating"),
  latencyMeaning: document.getElementById("latencyMeaning"),
  dnsAvg: document.getElementById("dnsAvg"),
  dnsFastest: document.getElementById("dnsFastest"),
  dnsRating: document.getElementById("dnsRating"),
  dnsMeaning: document.getElementById("dnsMeaning"),
  packetLoss: document.getElementById("packetLoss"),
  packetLossCounts: document.getElementById("packetLossCounts"),
  packetRating: document.getElementById("packetRating"),
  packetMeaning: document.getElementById("packetMeaning"),
  stabilityJitter: document.getElementById("stabilityJitter"),
  stabilityRating: document.getElementById("stabilityRating"),
  stabilityMeaning: document.getElementById("stabilityMeaning"),
  instabilityAlert: document.getElementById("instabilityAlert"),
  slowInternetInsight: document.getElementById("slowInternetInsight"),
  connectionIsp: document.getElementById("connectionIsp"),
  connectionLocation: document.getElementById("connectionLocation"),
  connectionIp: document.getElementById("connectionIp"),
  connectionServer: document.getElementById("connectionServer"),
};

function scoreColor(score) {
  if (score >= 80) return "#22c55e";
  if (score >= 50) return "#f59e0b";
  return "#ef4444";
}

function scoreLabel(score) {
  if (score >= 90) return "Excellent";
  if (score >= 75) return "Good";
  if (score >= 55) return "Moderate";
  if (score >= 35) return "Poor";
  return "Severe issues";
}

function numberOrDash(value, digits = 1) {
  if (typeof value !== "number" || Number.isNaN(value)) return "-";
  return value.toFixed(digits);
}

function speedUsageLabel(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "Unknown";
  if (value < 5) return "Very slow";
  if (value < 25) return "Basic";
  if (value <= 100) return "Good";
  return "Very fast";
}

function uploadUsageLabel(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "Unknown";
  if (value < 3) return "Limited";
  if (value <= 10) return "Moderate";
  return "Strong";
}

function speedMeaning(download, upload) {
  if (typeof download !== "number" || Number.isNaN(download)) {
    return "Speed data is unavailable. Retry diagnostics for a clearer speed profile.";
  }

  if (download < 5) {
    return "Suitable for basic browsing only. Streaming and multi-device usage may struggle.";
  }

  if (download < 25) {
    return "Good for browsing and single-device streaming. Multiple users may feel slowdowns.";
  }

  if (download <= 100) {
    if (typeof upload === "number" && !Number.isNaN(upload) && upload < 5) {
      return "Fast download for streaming, but limited upload can affect video calls and cloud backups.";
    }
    return "Strong for streaming, calls, and everyday multi-device use.";
  }

  return "Excellent for heavy streaming, large downloads, and multiple active users.";
}

function latencyQualityLabel(averageLatency) {
  if (typeof averageLatency !== "number" || Number.isNaN(averageLatency)) return "Unknown";
  if (averageLatency < 40) return "Excellent";
  if (averageLatency <= 80) return "Good";
  if (averageLatency <= 150) return "Moderate";
  return "Poor";
}

function latencyMeaning(avg) {
  if (typeof avg !== "number" || Number.isNaN(avg)) {
    return "Latency data is unavailable. Retry diagnostics for response-time insights.";
  }
  if (avg < 40) return "Responsive for gaming, calls, and real-time apps.";
  if (avg <= 80) return "Good for most browsing, streaming, and video calls.";
  if (avg <= 150) return "Usable, but lag may appear in calls, gaming, and remote work.";
  return "High delay likely to cause lag, buffering, and call quality issues.";
}

function qualityBadge(label) {
  const normalized = (label || "").toLowerCase();
  if (["excellent", "good", "very fast", "fast", "perfect", "very stable", "stable", "strong"].includes(normalized)) {
    return `🟢 ${label}`;
  }
  if (["moderate", "normal", "basic", "acceptable", "limited", "unstable"].includes(normalized)) {
    return `🟡 ${label}`;
  }
  return `🔴 ${label}`;
}

function maskIp(ip) {
  if (typeof ip !== "string" || !ip.trim()) return "-";
  const parts = ip.trim().split(".");
  if (parts.length === 4) {
    return `${parts[0]}.${parts[1]}.xxx.xxx`;
  }
  return ip;
}

function pickConnectionInfo(data) {
  const speed = data.speed || {};
  const analysis = data.analysis || {};
  const serverCandidate =
    speed.server?.name ||
    speed.best_server?.name ||
    speed.server ||
    analysis.server_used ||
    analysis.test_server ||
    null;

  return {
    isp: state.connectionInfo.isp || speed.isp || speed.client?.isp || analysis.isp || null,
    city: state.connectionInfo.city || speed.client?.city || analysis.location || null,
    ip: state.connectionInfo.ip || speed.client?.ip || analysis.ip_address || null,
    server: typeof serverCandidate === "string" ? serverCandidate : null,
  };
}

async function fetchConnectionInfo() {
  try {
    const response = await fetch("https://ipapi.co/json/");
    if (!response.ok) return;
    const data = await response.json();
    state.connectionInfo = {
      isp: data.org || data.org_name || null,
      city: data.city || null,
      ip: data.ip || null,
      server: null,
    };
  } catch (error) {
    state.connectionInfo = {
      isp: null,
      city: null,
      ip: null,
      server: null,
    };
  }
}

function metricLabelFromRules(metricName, value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "Unknown";

  if (metricName === "speed") {
    if (value < 5) return "Very slow";
    if (value < 25) return "Basic usage";
    if (value <= 100) return "Good";
    return "Very fast";
  }

  if (metricName === "latency") {
    if (value < 40) return "Excellent";
    if (value <= 80) return "Good";
    if (value <= 150) return "Moderate";
    return "Poor";
  }

  if (metricName === "stability") {
    if (value < 5) return "Very stable";
    if (value <= 20) return "Stable";
    if (value <= 50) return "Unstable";
    return "Highly unstable";
  }

  if (metricName === "dns") {
    if (value < 40) return "Fast";
    if (value <= 100) return "Normal";
    return "Slow";
  }

  if (metricName === "packet_loss") {
    if (value === 0) return "Perfect";
    if (value <= 2) return "Acceptable";
    if (value <= 5) return "Problematic";
    return "Severe issue";
  }

  return "Unknown";
}

function renderList(target, items, fallbackText) {
  target.innerHTML = "";
  if (!Array.isArray(items) || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = fallbackText;
    target.appendChild(li);
    return;
  }

  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    target.appendChild(li);
  });
}

function renderChecklist(checklist) {
  const items = Array.isArray(checklist)
    ? checklist.map((entry) => `${entry.ok ? "✔" : "•"} ${entry.label}`)
    : [];
  renderList(elements.healthChecklist, items, "Checklist will appear after diagnostics.");
}

function setLoaderStep(stepIndex) {
  elements.progressSteps.forEach((step, index) => {
    step.classList.remove("active", "completed");

    if (index < stepIndex) {
      step.classList.add("completed");
    } else if (index === stepIndex) {
      step.classList.add("active");
    }
  });

  elements.progressMessage.textContent = state.stagedMessages[stepIndex] || "Running diagnostics...";
}

function startProgressSimulation() {
  if (!elements.progressPanel || !elements.resultsSection) return;

  elements.progressPanel.classList.remove("hidden");
  elements.progressPanel.classList.remove("fading-out");
  elements.progressPanel.classList.add("is-visible");

  elements.resultsSection.classList.add("hidden");
  elements.resultsSection.classList.remove("is-visible");

  state.progressStepIndex = 0;

  if (state.progressTimer) {
    clearTimeout(state.progressTimer);
    state.progressTimer = null;
  }

  runProgressSteps();

  function runProgressSteps() {
    const maxIndex = state.stagedMessages.length - 1;
    const currentIndex = Math.min(state.progressStepIndex, maxIndex);
    setLoaderStep(currentIndex);

    const delay = state.stepDurations?.[currentIndex] || 1200;
    if (state.progressStepIndex < maxIndex) {
      state.progressStepIndex++;
    }

    state.progressTimer = setTimeout(runProgressSteps, delay);
  }
}

function completeProgressAndShowResults() {
  if (!elements.progressPanel || !elements.resultsSection) return;

  if (state.progressTimer) {
    clearTimeout(state.progressTimer);
    state.progressTimer = null;
  }

  setLoaderStep(state.stagedMessages.length - 1);

  elements.progressPanel.classList.add("fading-out");
  elements.progressPanel.classList.remove("is-visible");

  setTimeout(() => {
    elements.progressPanel.classList.add("hidden");
    elements.progressPanel.classList.remove("fading-out");

    elements.resultsSection.classList.remove("hidden");
    requestAnimationFrame(() => {
      elements.resultsSection.classList.add("is-visible");
    });
  }, 750);
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
  const pingData = data.ping || data.latency || {};
  const speed = data.speed || {};
  const latencySummary = pingData.summary || {};
  const dnsSummary = (data.dns || {}).summary || {};
  const packetLoss = data.packet_loss || {};
  const analysis = data.analysis || {};
  const metrics = analysis.metrics || {};

  const averageLatency =
    latencySummary.average_latency_ms ??
    latencySummary.average ??
    pingData.avg ??
    null;
  const minimumLatency =
    latencySummary.minimum_latency_ms ?? latencySummary.minimum ?? pingData.min ?? null;
  const maximumLatency =
    latencySummary.maximum_latency_ms ?? latencySummary.maximum ?? pingData.max ?? null;
  const jitter =
    latencySummary.jitter_ms ??
    latencySummary.jitter ??
    pingData.jitter ??
    (typeof minimumLatency === "number" && typeof maximumLatency === "number"
      ? maximumLatency - minimumLatency
      : null);
  const dnsAverage = dnsSummary.average_latency_ms ?? dnsSummary.average ?? (data.dns || {}).avg ?? null;
  const fastestServer = dnsSummary.fastest_server ?? (data.dns || {}).fastest ?? null;
  const packetLossValue = packetLoss.packet_loss_percent ?? packetLoss.percent ?? null;

  const healthScore = Number(analysis.health_score || 0);
  const connectionInfo = pickConnectionInfo(data);
  const downloadLabel = speedUsageLabel(speed.download_mbps);
  const uploadLabel = uploadUsageLabel(speed.upload_mbps);
  const latencyQuality = latencyQualityLabel(averageLatency);

  const instabilityHigh =
    (typeof jitter === "number" && jitter > 50) ||
    (typeof packetLossValue === "number" && packetLossValue >= 3);
  const slowFeelingLikely =
    instabilityHigh || (typeof averageLatency === "number" && averageLatency > 80);

  elements.healthScore.textContent = `${healthScore}`;
  elements.healthGrade.textContent = analysis.health_label || scoreLabel(healthScore);

  elements.connectionSummary.textContent =
    analysis.connection_summary ||
    "Your connection analysis is ready.";
  renderChecklist(analysis.checklist);

  elements.diagnosis.textContent = analysis.diagnosis || "No diagnosis available";
  elements.explanation.textContent = analysis.explanation || "No explanation available";
  elements.recommendation.textContent = analysis.recommendation || "No recommendation available.";
  renderList(
    elements.suggestionList,
    analysis.suggestions,
    "No urgent fixes needed. Run diagnostics again if conditions change."
  );

  elements.downloadSpeed.textContent = numberOrDash(speed.download_mbps, 2);
  elements.uploadSpeed.textContent = numberOrDash(speed.upload_mbps, 2);
  elements.latencyAvg.textContent = numberOrDash(averageLatency, 2);
  elements.latencyBest.textContent = numberOrDash(minimumLatency, 2);
  elements.latencyWorst.textContent = numberOrDash(maximumLatency, 2);
  elements.dnsAvg.textContent = numberOrDash(dnsAverage, 2);
  const dnsProviderName = (analysis.dns_provider || {}).name;
  elements.dnsFastest.textContent = dnsProviderName
    ? `Fastest provider: ${dnsProviderName}`
    : `Fastest: ${fastestServer || "-"}`;
  elements.packetLoss.textContent = numberOrDash(packetLossValue, 2);
  elements.packetLossCounts.textContent = `${packetLoss.packets_lost ?? "-"} lost of ${packetLoss.packets_sent ?? "-"}`;
  elements.stabilityJitter.textContent = numberOrDash(jitter, 2);
  elements.downloadLabel.textContent = `(${downloadLabel})`;
  elements.uploadLabel.textContent = `(${uploadLabel})`;

  elements.connectionIsp.textContent = connectionInfo.isp || "Not available";
  elements.connectionLocation.textContent = connectionInfo.city || "Not available";
  elements.connectionServer.textContent = connectionInfo.server || "Not available";
  elements.connectionIp.textContent = maskIp(connectionInfo.ip || "");

  const speedRating = metrics.speed?.rating || metricLabelFromRules("speed", speed.download_mbps);
  const latencyRating = metrics.latency?.rating || latencyQuality;
  const dnsRating = metrics.dns?.rating || metricLabelFromRules("dns", dnsAverage);
  const packetRating = metrics.packet_loss?.rating || metricLabelFromRules("packet_loss", packetLossValue);
  const stabilityRating = metrics.stability?.rating || metricLabelFromRules("stability", jitter);

  elements.speedRating.textContent = qualityBadge(speedRating);
  elements.latencyRating.textContent = qualityBadge(latencyRating);
  elements.dnsRating.textContent = qualityBadge(dnsRating);
  elements.packetRating.textContent = qualityBadge(packetRating);
  elements.stabilityRating.textContent = qualityBadge(stabilityRating);

  elements.speedMeaning.textContent = speedMeaning(speed.download_mbps, speed.upload_mbps);
  elements.latencyMeaning.textContent = latencyMeaning(averageLatency);
  elements.dnsMeaning.textContent =
    metrics.dns?.impact ||
    "DNS speed affects how quickly websites start loading.";
  elements.packetMeaning.textContent =
    metrics.packet_loss?.impact ||
    "Packet loss can cause buffering, call drops, and gaming lag.";
  elements.stabilityMeaning.textContent =
    metrics.stability?.meaning ||
    "High jitter means your connection fluctuates and may cause lag.";

  elements.instabilityAlert.classList.toggle("hidden", !instabilityHigh);
  elements.slowInternetInsight.classList.toggle("hidden", !slowFeelingLikely);

  renderGauge(healthScore);
}

async function runDiagnostics() {
  if (!elements.analyzeBtn) return;

  elements.analyzeBtn.disabled = true;
  elements.analyzeBtn.textContent = "Running...";
  startProgressSimulation();

  try {
    await fetchConnectionInfo();
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 90000);
    const response = await fetch(`${API_BASE}/diagnostics/full-analysis`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    renderResults(data);
    completeProgressAndShowResults();
  } catch (error) {
    elements.connectionSummary.textContent = "Diagnostics could not be completed.";
    renderList(elements.healthChecklist, [], "Checklist unavailable right now.");
    elements.diagnosis.textContent = "Analysis failed";
    elements.explanation.textContent =
      error && error.name === "AbortError"
        ? "Diagnostics timed out. Some network tests can be slow on hosted environments."
        : "Unable to complete diagnostics right now.";
    elements.recommendation.textContent = "Check backend logs and try again.";
    renderList(elements.suggestionList, [], "Retry in a moment.");
    completeProgressAndShowResults();
  } finally {
    elements.analyzeBtn.disabled = false;
    elements.analyzeBtn.textContent = "Analyze My Internet";
  }
}

const missingElements = REQUIRED_ELEMENT_KEYS.filter((key) => !elements[key]);
if (missingElements.length > 0) {
  console.error("FixMyInternet UI is missing required DOM elements:", missingElements);
} else {
  elements.analyzeBtn.addEventListener("click", runDiagnostics);
}
