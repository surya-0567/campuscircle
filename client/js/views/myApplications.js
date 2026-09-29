async function renderMyApplications(root) {
  let applications;
  try {
    applications = await api("/applications/mine");
  } catch (err) {
    root.innerHTML = emptyState("⚠️", "Couldn't load your applications", err.message);
    return;
  }

  if (applications.length === 0) {
    root.innerHTML = emptyState(
      "📋", "No applications yet",
      "Browse the feed and apply to opportunities that fit your skills.",
      `<a href="#/feed" class="btn btn-primary btn-sm">Browse Opportunities</a>`
    );
    return;
  }

  root.innerHTML = applications.map((a) => `
    <div class="list-row">
      <div class="avatar avatar-sm">${TYPE_ICONS[a.opportunity.type] || "📌"}</div>
      <div class="grow">
        <div class="title"><a href="#/opportunity/${a.opportunity.id}">${escapeHtml(a.opportunity.title)}</a></div>
        <div class="sub">${escapeHtml(a.opportunity.organization)} · Applied ${timeAgo(a.applied_at)} · Deadline ${formatDeadline(a.opportunity.deadline)}</div>
      </div>
      ${statusBadge(a.status)}
      <div class="actions">
        ${a.status === "applied" ? `<button class="btn btn-sm btn-ghost withdraw-btn" data-id="${a.id}">Withdraw</button>` : ""}
      </div>
    </div>
  `).join("");

  root.querySelectorAll(".withdraw-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!confirm("Withdraw this application?")) return;
      try {
        await api(`/applications/${btn.dataset.id}`, { method: "DELETE" });
        toast("Application withdrawn.", "info");
        renderMyApplications(root);
      } catch (err) {
        toast(err.message, "error");
      }
    });
  });
}
