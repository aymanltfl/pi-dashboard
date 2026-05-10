// ─── AUTH ────────────────────────────────────────────────────────────────────
const token = localStorage.getItem("token");
if (!token) { window.location.href = "/login.html"; }

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "/login.html";
}

document.addEventListener("DOMContentLoaded", () => {
  const user = localStorage.getItem("user");
  if (user) {
    const el = document.getElementById("welcome");
    if (el) el.textContent = user;
  }
  document.getElementById("chat-input").addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
  });
});

// ─── DARK MODE ────────────────────────────────────────────────────────────────
const darkToggle = document.getElementById("dark-toggle");
const savedTheme = localStorage.getItem("theme");

if (savedTheme === "light") {
  document.body.classList.remove("dark");
} else {
  document.body.classList.add("dark");
}

darkToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  localStorage.setItem("theme", document.body.classList.contains("dark") ? "dark" : "light");
});
// Mobile controls
const darkToggleMobile = document.getElementById("dark-toggle-mobile");
const langToggleMobile = document.getElementById("lang-toggle-mobile");

if (darkToggleMobile) {
  darkToggleMobile.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    localStorage.setItem("theme", document.body.classList.contains("dark") ? "dark" : "light");
  });
}

if (langToggleMobile) {
  langToggleMobile.addEventListener("click", () => {
    applyLang(currentLang === "de" ? "en" : "de");
  });
}
// ─── LANGUAGE ────────────────────────────────────────────────────────────────
let currentLang = localStorage.getItem("lang") || "de";
const langToggle = document.getElementById("lang-toggle");

function applyLang(lang) {
  document.querySelectorAll("[data-de]").forEach(el => {
    el.textContent = el.dataset[lang] || el.dataset.de;
  });
  document.querySelectorAll("[data-de][placeholder]").forEach(el => {
    el.placeholder = lang === "en" ? "Ask an IT question..." : "IT-Frage stellen...";
  });
  langToggle.textContent = lang === "de" ? "DE/EN" : "EN/DE";
  currentLang = lang;
  localStorage.setItem("lang", lang);
}

langToggle.addEventListener("click", () => {
  applyLang(currentLang === "de" ? "en" : "de");
});

applyLang(currentLang);

// ─── SIDEBAR NAV ─────────────────────────────────────────────────────────────
const navLinks = document.querySelectorAll(".nav-link");
navLinks.forEach(link => {
  link.addEventListener("click", () => {
    navLinks.forEach(l => l.classList.remove("active"));
    link.classList.add("active");
  });
});

// ─── ACCORDION ───────────────────────────────────────────────────────────────
function toggleProject(id) {
  const body = document.getElementById(id);
  const arrow = document.getElementById("arrow-" + id);
  body.classList.toggle("open");
  arrow.classList.toggle("open");
}

// ─── SYSTEM STATUS ────────────────────────────────────────────────────────────
async function loadStatus() {
  try {
    const res = await fetch("/api/status");
    const d = await res.json();
    document.getElementById("temp").textContent = d.temp + " °C";
    const load = d.cpu_load;
    document.getElementById("cpu").textContent = load;
    const cpuPct = Math.min((load / 4) * 100, 100);
    document.getElementById("cpu-bar").style.width = cpuPct + "%";
    const ramPct = Math.round((d.ram_used / d.ram_total) * 100);
    document.getElementById("ram").textContent = d.ram_used + " / " + d.ram_total + " MB";
    document.getElementById("ram-bar").style.width = ramPct + "%";
  } catch {
    document.getElementById("temp").textContent = "offline";
  }
  try {
    const res = await fetch("/api/uptime");
    const d = await res.json();
    document.getElementById("uptime").textContent = d.uptime;
  } catch {}
}

// ─── ENERGY TOTALS ────────────────────────────────────────────────────────────
async function loadTotals() {
  try {
    const res = await fetch("/api/energy_total");
    const d = await res.json();
    const parts = d.runtime.split(":");
    const days = parseInt(parts[0]);
    const hours = parseInt(parts[1]);
    const mins = parseInt(parts[2]);
    let rt = "";
    if (days > 0) rt += days + "T ";
    if (days > 0 || hours > 0) rt += hours + "Std. ";
    rt += mins + "Min.";
    document.getElementById("total-runtime").textContent = rt.trim();
    document.getElementById("total-kwh").textContent = d.total_kwh + " kWh";
    document.getElementById("total-cost").textContent = d.total_cost + " €";
    const co2g = Math.round(d.total_co2 * 1000 * 10) / 10;
    document.getElementById("total-co2").textContent = co2g + " g CO₂";
    document.getElementById("total-since").textContent = d.start_date;
  } catch {}
}

// ─── PIHOLE ───────────────────────────────────────────────────────────────────
let piholeToken = null;

async function getPiholeToken() {
  try {
    const res = await fetch("/pihole-api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: "p0cQP-lW" })
    });
    const d = await res.json();
    if (d.session && d.session.valid) piholeToken = d.session.sid;
  } catch {}
}

async function loadPihole() {
  try {
    if (!piholeToken) await getPiholeToken();
    const res = await fetch("/pihole-api/stats/summary", {
      headers: { "sid": piholeToken }
    });
    if (res.status === 401) { piholeToken = null; await getPiholeToken(); return; }
    const d = await res.json();
    document.getElementById("ph-total").textContent = d.queries.total.toLocaleString();
    document.getElementById("ph-blocked").textContent = d.queries.blocked.toLocaleString();
    const pct = d.queries.percent_blocked.toFixed(1);
    document.getElementById("ph-percent").textContent = pct + " %";
    document.getElementById("ph-bar").style.width = Math.min(pct, 100) + "%";
    document.getElementById("ph-gravity").textContent = d.gravity.domains_being_blocked.toLocaleString();
    document.getElementById("ph-clients").textContent = d.clients.active;
    document.getElementById("ph-cache").textContent = d.queries.cached.toLocaleString();
  } catch {}
}

// ─── CHAT ─────────────────────────────────────────────────────────────────────
let chatHistory = [];

function toggleChat() {
  document.getElementById("chat-window").classList.toggle("open");
}

async function sendMessage() {
  const input = document.getElementById("chat-input");
  const messages = document.getElementById("chat-messages");
  const text = input.value.trim();
  if (!text) return;

  messages.innerHTML += `<div class="bubble-user">${text}</div>`;
  input.value = "";
  messages.scrollTop = messages.scrollHeight;

  const typingId = "typing-" + Date.now();
  messages.innerHTML += `<div class="bubble-bot" id="${typingId}">...</div>`;
  chatHistory.push({ role: "user", content: text });

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: chatHistory })
    });
    const d = await res.json();
    chatHistory.push({ role: "assistant", content: d.reply });
    const formatted = d.reply
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
    document.getElementById(typingId).outerHTML = `<div class="bubble-bot">${formatted}</div>`;
  } catch {
    chatHistory.pop();
    document.getElementById(typingId).outerHTML = `<div class="bubble-bot" style="color:#c0392b;">Bot offline</div>`;
  }
  messages.scrollTop = messages.scrollHeight;
}

// ─── INTERVALS ────────────────────────────────────────────────────────────────
setInterval(loadStatus, 2000);
setInterval(loadTotals, 60000);
setInterval(loadPihole, 30000);

loadStatus();
loadTotals();
loadPihole();

// ─── UPTIME KUMA ──────────────────────────────────────────────────────────────
async function loadUptime() {
  try {
    const [pageRes, hbRes] = await Promise.all([
      fetch("/uptime-api/status-page/pi"),
      fetch("/uptime-api/status-page/heartbeat/pi")
    ]);
    const page = await pageRes.json();
    const hb = await hbRes.json();

    const monitors = page.publicGroupList?.[0]?.monitorList || [];
    const grid = document.getElementById("uptime-grid");

    grid.innerHTML = monitors.map(m => {
      const beats = hb.heartbeatList?.[m.id] || [];
      const last = beats[beats.length - 1];
      const online = last?.status === 1;
      const ping = last?.ping ? last.ping + "ms" : "–";
      const uptime = hb.uptimeList?.[m.id + "_24"];
      const uptimePct = uptime !== undefined ? (uptime * 100).toFixed(1) + "%" : "–";
      return `
        <div class="metric-card ${online ? "" : ""}">
          <div class="metric-label">${m.name}</div>
          <div class="metric-value mono" style="color:${online ? "var(--green)" : "#e74c3c"};font-size:0.9rem;">
            ${online ? "● Online" : "● Offline"}
          </div>
          <div style="font-size:0.7rem;color:var(--text2);margin-top:6px;font-family:var(--mono);">
            ${ping} · ${uptimePct} uptime
          </div>
        </div>`;
    }).join("");
  } catch {
    document.getElementById("uptime-grid").innerHTML = "<div style='color:var(--text2);font-size:0.85rem;'>Uptime Kuma offline</div>";
  }
}

setInterval(loadUptime, 60000);
loadUptime();

let networkData = { device_count: 0, services: {} };

async function loadNetworkData() {
  try {
    const res = await fetch("/api/network");
    networkData = await res.json();
  } catch {}
}

setInterval(loadNetworkData, 30000);
loadNetworkData();
// ─── PIHOLE EVENTS ────────────────────────────────────────────────────────────
let lastBlocked = null;

async function checkPiholeEvents() {
  try {
    if (!piholeToken) await getPiholeToken();
    const res = await fetch("/pihole-api/stats/summary", {
      headers: { "sid": piholeToken }
    });
    if (res.status === 401) { piholeToken = null; return; }
    const d = await res.json();
    const blocked = d.queries.blocked;
    if (lastBlocked !== null && blocked > lastBlocked) {
      const diff = blocked - lastBlocked;
      // Mehrere Ripples je nach Anzahl neuer Blocks
      const count = Math.min(diff, 3);
      for (let i = 0; i < count; i++) {
        setTimeout(() => rippleNode("pihole", "#ef4444"), i * 300);
      }
    }
    lastBlocked = blocked;
  } catch {}
}

setInterval(checkPiholeEvents, 5000);
checkPiholeEvents();

// ─── D3 NETWORK DIAGRAM ───────────────────────────────────────────────────────
function initNetwork() {
  const container = document.getElementById("network-svg");
  if (!container) return;

  const rect = container.parentElement.getBoundingClientRect();
  const width = rect.width - 55;
  const height = 300;

  const svg = d3.select("#network-svg")
    .attr("width", width)
    .attr("height", height);

  // ─── NODES ──────────────────────────────────────────────────────────────────

const nodes = [
    { id: "visitor",  label: "Web Besucher",  group: "external", icon: "👤", fx: width*0.15, fy: height*0.2 },
    { id: "internet", label: "Internet",       group: "external", icon: "🌐", fx: width*0.5,  fy: height*0.2 },
    { id: "pihole",   label: "Pi-hole",        group: "service",  icon: "🛡", fx: width*0.9,  fy: height*0.2 },
    { id: "local",    label: "Lokale Clients", group: "external", icon: "🏠", fx: width*0.2, fy: height*0.8 },
    { id: "fritzbox", label: "Fritz!Box",      group: "network",  icon: "📡", fx: width*0.5,  fy: height*0.8 },
    { id: "pi",       label: "Raspberry Pi",   group: "server",   icon: "🖥",  fx: width*0.9,  fy: height*0.8 },
];

  // ─── LINKS ──────────────────────────────────────────────────────────────────
const links = [
    { source: "visitor",  target: "internet", type: "wan"     },
    { source: "internet", target: "fritzbox", type: "wan"     },
    { source: "pihole",   target: "internet", type: "dns"     },
    { source: "pi",       target: "pihole",   type: "service" },
    { source: "local",    target: "fritzbox", type: "lan"     },
    { source: "fritzbox", target: "pi",       type: "lan"     },
];

  // ─── FARBEN ─────────────────────────────────────────────────────────────────
  const groupColors = {
    external: "#ffffff",
    network:  "#edf043",
    server:   "#aa3365",
    service:  "#951717",
    cloud:    "#444c56"
  };

  const linkColors = {
    lan:     "#2d7d7d",
    wan:     "#f59e0b",
    service: "#4a9ead",
    cloud:   "#555",
    dns:     "#27ae60"
  };

  // ─── FORCE SIMULATION ───────────────────────────────────────────────────────
  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(120))
    .force("charge", d3.forceManyBody().strength(-400))
    .force("center", d3.forceCenter(width * 0.48, height / 2).strength(0.3))
    .force("collision", d3.forceCollide(50));

  // ─── LINKS ──────────────────────────────────────────────────────────────────
  const link = svg.append("g")
    .selectAll("line")
    .data(links)
    .enter()
    .append("line")
    .attr("stroke", d => linkColors[d.type] || "#555")
    .attr("stroke-width", 4)
    .attr("stroke-opacity", 0.4)
    .attr("stroke-dasharray", d => d.type === "cloud" ? "4,4" : "none");

  // ─── NODE GROUPS ────────────────────────────────────────────────────────────
  const nodeGroup = svg.append("g")
    .selectAll("g")
    .data(nodes)
    .enter()
    .append("g")
    .attr("class", d => "node node-" + d.id)


  // ─── TOOLTIP ────────────────────────────────────────────────────────────────
  const tooltip = d3.select("body").append("div")
    .style("position", "fixed")
    .style("background", "#1a1f2a")
    .style("border", "1px solid #2d7d7d")
    .style("border-radius", "8px")
    .style("padding", "8px 12px")
    .style("font-size", "11px")
    .style("font-family", "JetBrains Mono, monospace")
    .style("color", "#e6edf3")
    .style("pointer-events", "none")
    .style("opacity", 0)
    .style("z-index", 9999);

  nodeGroup
    .on("mouseover", function(event, d) {
      let content = `<strong>${d.label}</strong>`;
      if (d.id === "local") {
        content += `<br>${networkData.device_count} Geräte im Netz`;
      }
      tooltip
        .html(content)
        .style("opacity", 1)
        .style("left", (event.clientX + 12) + "px")
        .style("top", (event.clientY - 8) + "px");
    })
    .on("mousemove", function(event) {
      tooltip
        .style("left", (event.clientX + 12) + "px")
        .style("top", (event.clientY - 8) + "px");
    })
    .on("mouseout", function() {
      tooltip.style("opacity", 0);
    });
  // ─── NODE CIRCLES ───────────────────────────────────────────────────────────
  nodeGroup.append("circle")
    .attr("r", 24)
    .attr("fill", d => groupColors[d.group] || "#2d7d7d")
    .attr("stroke", "#0d1117")
    .attr("stroke-width", 2);

  // ─── NODE ICONS ─────────────────────────────────────────────────────────────
  nodeGroup.append("text")
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .attr("font-size", "25px")
    .text(d => d.icon);

  // ─── NODE LABELS ────────────────────────────────────────────────────────────
  nodeGroup.append("text")
      .attr("text-anchor", "middle")
      .attr("dy", 38)
      .attr("font-size", "13px")
      .attr("font-family", "DM Sans, sans-serif")
      .attr("fill", "#000000")
      .attr("paint-order", "stroke")
      .attr("stroke", "#ffffff56")
      .attr("stroke-width", "2px")
      .attr("stroke-linejoin", "round")
      .text(d => d.label);

  // ─── TICK ───────────────────────────────────────────────────────────────────
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    nodeGroup.attr("transform", d => `translate(${d.x},${d.y})`);
  });

  // ─── HEARTBEAT ──────────────────────────────────────────────────────────────
  function heartbeat() {
    nodeGroup.selectAll("circle")
      .transition()
      .duration(300)
      .attr("r", 28)
      .transition()
      .duration(500)
      .attr("r", 24);
  }

  setInterval(heartbeat, 30000);

  // ─── PARTICLE FLOW ──────────────────────────────────────────────────────────
  window.networkEmit = function(sourceId, targetId, color) {
    const sourceNode = nodes.find(n => n.id === sourceId);
    const targetNode = nodes.find(n => n.id === targetId);
    if (!sourceNode || !targetNode) return;

    const particle = svg.append("circle")
      .attr("r", 5)
      .attr("fill", color || "#2d7d7d")
      .attr("cx", sourceNode.x)
      .attr("cy", sourceNode.y);

    particle.transition()
      .duration(1000)
      .ease(d3.easeLinear)
      .attr("cx", targetNode.x)
      .attr("cy", targetNode.y)
      .on("end", () => particle.remove());
  };

  // ─── NODE PULSE ─────────────────────────────────────────────────────────────
  window.networkPulse = function(nodeId, color) {
    const n = svg.select(".node-" + nodeId).select("circle");
    if (n.empty()) return;
    n.transition().duration(200).attr("r", 32).attr("fill", color)
     .transition().duration(600).attr("r", 28).attr("fill", d => groupColors[d.group] || "#2d7d7d");
  };
// ─── RIPPLE ─────────────────────────────────────────────────────────────────
  window.rippleNode = function(nodeId, color) {
    const targetNode = nodes.find(n => n.id === nodeId);
    if (!targetNode) return;

    const ripple = svg.append("circle")
      .attr("cx", targetNode.fx)
      .attr("cy", targetNode.fy)
      .attr("r", 28)
      .attr("fill", "none")
      .attr("stroke", color)
      .attr("stroke-width", 2)
      .attr("opacity", 0.8);

    ripple.transition()
      .duration(1000)
      .ease(d3.easeLinear)
      .attr("r", 60)
      .attr("opacity", 0)
      .on("end", () => ripple.remove());
  };

}

// Init wenn DOM ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initNetwork);
} else {
  initNetwork();
}
