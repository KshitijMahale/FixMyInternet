function simulateProgress() {
  const loading = document.getElementById("loading");
  const steps = [
    "Testing Speed...",
    "Testing Latency...",
    "Testing DNS...",
    "Checking Packet Loss...",
    "Analyzing Connection...",
  ];

  let step = 0;

  return setInterval(() => {
    if (step < steps.length) {
      loading.innerText = steps[step];
      step++;
    }
  }, 1200);
}

const btn = document.getElementById("analyzeBtn");

btn.addEventListener("click", async () => {
  const loading = document.getElementById("loading");

  try {
    btn.innerText = "Analyzing...";
    btn.disabled = true;
    loading.classList.remove("hidden");

    const progressInterval = simulateProgress();

    const response = await fetch(
      "http://127.0.0.1:8000/diagnostics/full-analysis",
    );

    const data = await response.json();

    document.getElementById("results").classList.remove("hidden");

    // Health Score
    const score = data.analysis.health_score;

    document.getElementById("healthScore").innerText = score;

    const circle = document.getElementById("scoreCircle");
    const circumference = 440;
    const offset = circumference - (score / 100) * circumference;
    circle.style.strokeDashoffset = offset;

    if (score >= 80) {
      circle.style.stroke = "#22c55e";
    } else if (score >= 50) {
      circle.style.stroke = "#facc15";
    } else {
      circle.style.stroke = "#ef4444";
    }

    // Speed
    document.getElementById("download").innerText =
      data.speed.download_mbps ?? "N/A";

    document.getElementById("upload").innerText =
      data.speed.upload_mbps ?? "N/A";

    // Packet Loss
    document.getElementById("packetLoss").innerText =
      data.packet_loss.packet_loss_percent ?? "N/A";

    // Diagnosis
    document.getElementById("diagnosis").innerText = data.analysis.diagnosis;

    document.getElementById("explanation").innerText =
      data.analysis.explanation;

    document.getElementById("recommendation").innerText =
      data.analysis.recommendation;

    // Latency
    const latencyList = document.getElementById("latencyResults");
    latencyList.innerHTML = "";

    for (const [server, value] of Object.entries(data.ping)) {
      const li = document.createElement("li");

      li.innerText = `${server}: ${value ? value + " ms" : "N/A"}`;

      latencyList.appendChild(li);
    }

    // DNS
    const dnsList = document.getElementById("dnsResults");
    dnsList.innerHTML = "";

    for (const [provider, value] of Object.entries(data.dns)) {
      const li = document.createElement("li");

      li.innerText = `${provider}: ${value ? value + " ms" : "N/A"}`;

      dnsList.appendChild(li);
    }
  } catch (error) {
    console.error("Diagnostics failed:", error);
    alert("Diagnostics failed. Check console.");
  } finally {
    clearInterval(progressInterval);
    loading.classList.add("hidden");
    btn.innerText = "Analyze My Internet";
    btn.disabled = false;
  }
});
