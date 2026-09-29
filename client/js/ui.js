// Small reusable UI-building helpers shared across views.

function emptyState(icon, title, message, actionHtml = "") {
  return `
    <div class="empty-state">
      <div class="ic">${icon}</div>
      <h3>${escapeHtml(title)}</h3>
      <p>${escapeHtml(message)}</p>
      ${actionHtml}
    </div>
  `;
}

function loadingRow(label = "Loading...") {
  return `<div class="loading-row"><div class="spinner"></div> ${escapeHtml(label)}</div>`;
}

function skillChips(skills, cls = "chip-skill") {
  if (!skills || skills.length === 0) return `<span class="text-muted text-sm">None listed</span>`;
  return `<div class="chip-list">${skills.map((s) => `<span class="chip ${cls}">${escapeHtml(s)}</span>`).join("")}</div>`;
}

function statusBadge(status) {
  const map = {
    applied: ["Applied", "badge-applied"],
    shortlisted: ["Shortlisted", "badge-shortlisted"],
    selected: ["Selected", "badge-selected"],
    rejected: ["Not Selected", "badge-rejected"],
    open: ["Open", "badge-open"],
    closed: ["Closed", "badge-closed"],
  };
  const [label, cls] = map[status] || [status, "badge-type"];
  return `<span class="badge ${cls}">${label}</span>`;
}

function matchBadgeHtml(score) {
  if (score == null) return "";
  return `<div class="match-badge"><div class="pct">${score}%</div><div class="lbl">Match</div></div>`;
}

function oppMetaRow(opp) {
  const items = [
    `<span class="item">${TYPE_ICONS[opp.type] || "📌"} ${TYPE_LABELS[opp.type] || opp.type}</span>`,
    `<span class="item">${MODE_ICONS[opp.mode] || ""} ${opp.mode}</span>`,
    `<span class="item">📍 ${opp.distance_km != null ? opp.distance_km + " km" : escapeHtml(opp.city || "—")}</span>`,
    `<span class="item">${opp.paid ? "💰 " + (escapeHtml(opp.stipend) || "Paid") : "🆓 Unpaid"}</span>`,
  ];
  return `<div class="opp-meta-row">${items.join("")}</div>`;
}

function oppCardHtml(opp, opts = {}) {
  const closingSoon = opp.is_closing_soon;
  const bookmarkIcon = opp.is_bookmarked ? "★" : "☆";
  return `
    <div class="opp-card" data-id="${opp.id}">
      <div class="head">
        <div>
          <div class="title">${escapeHtml(opp.title)} ${opp.is_referral ? '<span class="badge badge-referral">Alumni Referral</span>' : ""}</div>
          <div class="org">${escapeHtml(opp.organization || opp.poster?.college || "")}</div>
        </div>
        ${matchBadgeHtml(opp.match_score)}
      </div>
      ${oppMetaRow(opp)}
      <div class="flex items-center gap-8" style="flex-wrap:wrap;">
        ${closingSoon ? '<span class="badge badge-urgent">⏰ Closing soon</span>' : ""}
        <span class="text-sm text-muted">Deadline: ${formatDeadline(opp.deadline)}</span>
        <span class="text-sm text-muted">· ${opp.application_count} applicant(s)</span>
      </div>
      ${opts.showReasons && opp.match_reasons && opp.match_reasons.length ? `
        <div class="match-reasons"><ul>${opp.match_reasons.slice(0, 3).map((r) => `<li>${escapeHtml(r)}</li>`).join("")}</ul></div>
      ` : ""}
      <div class="foot">
        <a href="#/opportunity/${opp.id}" class="btn btn-primary btn-sm">View Details</a>
        <button class="btn btn-ghost btn-sm bookmark-btn" data-id="${opp.id}" data-active="${opp.is_bookmarked}">${bookmarkIcon} Save</button>
        ${opp.has_applied ? '<span class="badge badge-applied" style="align-self:center;">Applied</span>' : ""}
      </div>
    </div>
  `;
}

function wireBookmarkButtons(root, onChange) {
  root.querySelectorAll(".bookmark-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      const active = btn.dataset.active === "true";
      try {
        if (active) {
          await api(`/bookmarks/${id}`, { method: "DELETE" });
          toast("Removed from bookmarks.", "info");
        } else {
          await api(`/bookmarks/${id}`, { method: "POST" });
          toast("Saved to your bookmarks.", "success");
        }
        if (onChange) onChange();
        else {
          btn.dataset.active = (!active).toString();
          btn.textContent = !active ? "★ Save" : "☆ Save";
        }
      } catch (err) {
        toast(err.message, "error");
      }
    });
  });
}

function modal(html) {
  const backdrop = document.createElement("div");
  backdrop.className = "modal-backdrop";
  backdrop.innerHTML = `<div class="modal-box">${html}</div>`;
  backdrop.addEventListener("click", (e) => {
    if (e.target === backdrop) backdrop.remove();
  });
  document.body.appendChild(backdrop);
  return backdrop;
}
