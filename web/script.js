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
