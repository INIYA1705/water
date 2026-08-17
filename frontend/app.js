const API = "";

let consumptionChart, flowChart, peakChart, qualityChart;

async function fetchJSON(path) {
  const res = await fetch(`${API}${path}`);
  return res.json();
}

function formatTime(iso) {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function setQualityBar(data) {
  const bar = document.getElementById("qualityBar");
  const labels = { good: "All systems normal", warning: "Quality warning", critical: "LEAK DETECTED", unknown: "No data" };
  bar.className = `status-bar status-${data.status}`;
  bar.textContent = data.issues.length ? data.issues.join(" | ") : labels[data.status];
}

function updateCards(summary) {
  const latest = summary.latest_reading || {};
  document.getElementById("totalConsumption").textContent = summary.total_consumption_liters ?? "—";
  document.getElementById("flowRate").textContent = latest.flow_rate ?? "—";
  document.getElementById("pressure").textContent = latest.water_pressure ?? "—";
  document.getElementById("cost").textContent = summary.estimated_cost_inr ?? "—";
  document.getElementById("ph").textContent = latest.ph ?? "—";
  document.getElementById("turbidity").textContent = latest.turbidity ?? "—";
}

function buildCharts(readings, peaks) {
  const sorted = [...readings].reverse();
  const labels = sorted.map(r => formatTime(r.created_at));

  if (consumptionChart) consumptionChart.destroy();
  consumptionChart = new Chart(document.getElementById("consumptionChart"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Consumption (L)",
        data: sorted.map(r => r.water_consumption),
        borderColor: "#38bdf8",
        tension: 0.3,
        fill: false,
      }],
    },
    options: { responsive: true, plugins: { legend: { labels: { color: "#94a3b8" } } },
      scales: { x: { ticks: { color: "#64748b" } }, y: { ticks: { color: "#64748b" } } } },
  });

  if (flowChart) flowChart.destroy();
  flowChart = new Chart(document.getElementById("flowChart"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Flow Rate (L/min)",
        data: sorted.map(r => r.flow_rate),
        borderColor: "#22d3ee",
        tension: 0.3,
      }],
    },
    options: { responsive: true, plugins: { legend: { labels: { color: "#94a3b8" } } },
      scales: { x: { ticks: { color: "#64748b" } }, y: { ticks: { color: "#64748b" } } } },
  });

  if (peakChart) peakChart.destroy();
  peakChart = new Chart(document.getElementById("peakChart"), {
    type: "bar",
    data: {
      labels: peaks.map(p => p.label),
      datasets: [{
        label: "Avg Flow (L/min)",
        data: peaks.map(p => p.avg_flow_rate),
        backgroundColor: "#0284c7",
      }],
    },
    options: { responsive: true, plugins: { legend: { labels: { color: "#94a3b8" } } },
      scales: { x: { ticks: { color: "#64748b" } }, y: { ticks: { color: "#64748b" } } } },
  });

  if (qualityChart) qualityChart.destroy();
  qualityChart = new Chart(document.getElementById("qualityChart"), {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "pH", data: sorted.map(r => r.ph), borderColor: "#a78bfa", tension: 0.3 },
        { label: "Turbidity (NTU)", data: sorted.map(r => r.turbidity), borderColor: "#fbbf24", tension: 0.3 },
      ],
    },
    options: { responsive: true, plugins: { legend: { labels: { color: "#94a3b8" } } },
      scales: { x: { ticks: { color: "#64748b" } }, y: { ticks: { color: "#64748b" } } } },
  });
}

function renderAlerts(alerts) {
  const list = document.getElementById("alertsList");
  if (!alerts.length) {
    list.innerHTML = "<li>No alerts</li>";
    return;
  }
  list.innerHTML = alerts.slice(0, 10).map(a =>
    `<li class="${a.severity}">[${a.alert_type.toUpperCase()}] ${a.message}</li>`
  ).join("");
}

function renderROI(roi) {
  document.getElementById("roiDetails").innerHTML = `
    <div><span>Hardware Cost</span><strong>₹${roi.hardware_cost_inr}</strong></div>
    <div><span>Software Cost</span><strong>₹${roi.software_cost_inr}/mo</strong></div>
    <div><span>Monthly Savings</span><strong>₹${roi.estimated_monthly_savings_inr}</strong></div>
    <div><span>Payback Period</span><strong>${roi.payback_period_months} months</strong></div>
  `;
}

async function refresh() {
  try {
    const [readings, summary, peaks, quality, alerts, roi] = await Promise.all([
      fetchJSON("/api/readings"),
      fetchJSON("/api/summary"),
      fetchJSON("/api/peaks"),
      fetchJSON("/api/quality"),
      fetchJSON("/api/alerts"),
      fetchJSON("/api/roi"),
    ]);

    if (summary.message) {
      document.getElementById("qualityBar").textContent = summary.message;
      return;
    }

    setQualityBar(quality);
    updateCards(summary);
    buildCharts(readings, peaks);
    renderAlerts(alerts);
    renderROI(roi);
  } catch (err) {
    console.error(err);
    document.getElementById("qualityBar").textContent = "Cannot reach API. Start backend: python backend/api.py";
  }
}

document.getElementById("syncBtn").addEventListener("click", async () => {
  const btn = document.getElementById("syncBtn");
  btn.textContent = "Syncing...";
  try {
    const res = await fetch("/api/sync", { method: "POST" });
    const data = await res.json();
    if (data.status === "ok") {
      btn.textContent = `Synced ${data.synced} readings`;
    } else {
      btn.textContent = "Sync failed";
      alert(data.message || "Sync failed. Check .env keys.");
    }
  } catch {
    btn.textContent = "Sync failed";
    alert("Cannot reach backend. Is api.py running?");
  }
  setTimeout(() => { btn.textContent = "Sync from ThingSpeak"; }, 3000);
  refresh();
});

refresh();
setInterval(refresh, 30000);
