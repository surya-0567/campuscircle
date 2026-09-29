// Central place for talking to the backend REST API.
const API_BASE = "/api";

function getToken() {
  return localStorage.getItem("cc_token");
}
function setSession(token, user) {
  localStorage.setItem("cc_token", token);
  localStorage.setItem("cc_user", JSON.stringify(user));
}
function getCachedUser() {
  try {
    return JSON.parse(localStorage.getItem("cc_user") || "null");
  } catch {
    return null;
  }
}
function clearSession() {
  localStorage.removeItem("cc_token");
  localStorage.removeItem("cc_user");
}

async function api(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  let res;
  try {
    res = await fetch(API_BASE + path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (err) {
    throw new Error("Can't reach the server. Is the backend running?");
  }

  let data = {};
  const text = await res.text();
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    // no/invalid JSON body
  }

  if (res.status === 401 && auth) {
    clearSession();
    window.location.href = "/login";
    throw new Error("Session expired. Please log in again.");
  }

  if (!res.ok) {
    let message = data.detail || `Request failed (${res.status})`;
    if (Array.isArray(data.detail)) {
      // FastAPI validation error format
      message = data.detail.map((d) => d.msg).join(", ");
    }
    throw new Error(message);
  }
  return data;
}

// ---------- Toasts ----------
function toast(message, type = "info") {
  let root = document.getElementById("toast-root");
  if (!root) {
    root = document.createElement("div");
    root.id = "toast-root";
    document.body.appendChild(root);
  }
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  root.appendChild(el);
  setTimeout(() => el.remove(), 3800);
}

function initials(name) {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/);
  return (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
}

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function daysUntil(dateStr) {
  const d = new Date(dateStr + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.round((d - today) / 86400000);
}

function formatDeadline(dateStr) {
  const days = daysUntil(dateStr);
  const d = new Date(dateStr + "T00:00:00");
  const formatted = d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  if (days < 0) return `Closed (${formatted})`;
  if (days === 0) return `Today!`;
  if (days === 1) return `Tomorrow`;
  if (days <= 3) return `${formatted} (${days}d left)`;
  return formatted;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str == null ? "" : String(str);
  return div.innerHTML;
}

const TYPE_ICONS = { internship: "💼", project: "🛠️", hackathon: "🚀", freelance: "💸" };
const TYPE_LABELS = { internship: "Internship", project: "Project", hackathon: "Hackathon", freelance: "Freelance" };
const MODE_ICONS = { online: "🌐", offline: "📍", hybrid: "🔀" };
