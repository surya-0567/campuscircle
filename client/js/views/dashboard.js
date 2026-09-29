async function renderDashboard(root) {
  const user = getCachedUser();

  let feed = [];
  let applications = [];
  let bookmarks = [];
  try {
    [feed, applications, bookmarks] = await Promise.all([
      api("/opportunities/feed?sort=match"),
      api("/applications/mine"),
      api("/bookmarks"),
    ]);
  } catch (err) {
    root.innerHTML = emptyState("⚠️", "Couldn't load your dashboard", err.message);
    return;
  }

  const closingSoonCount = feed.filter((o) => o.is_closing_soon).length;
  const topMatches = feed.slice(0, 4);
  const roleNote = user.role === "alumni"
    ? "As an alumni, you can post referrals to help juniors from your college."
    : "Here's what's happening in your CampusCircle today.";

  root.innerHTML = `
    <div class="welcome-banner">
      <div>
        <h2>Welcome back, ${escapeHtml(user.name.split(" ")[0])} 👋</h2>
        <p>${escapeHtml(roleNote)}</p>
      </div>
      <a href="#/feed" class="btn btn-accent">🧭 Browse Feed</a>
    </div>

    <div class="stat-grid">
      <div class="stat-card"><div class="v">${feed.length}</div><div class="l">Open Matches</div></div>
      <div class="stat-card"><div class="v">${closingSoonCount}</div><div class="l">Closing Soon</div></div>
      <div class="stat-card"><div class="v">${applications.length}</div><div class="l">Applications</div></div>
      <div class="stat-card"><div class="v">${bookmarks.length}</div><div class="l">Saved</div></div>
      <div class="stat-card"><div class="v">${user.skills.length}</div><div class="l">Skills Listed</div></div>
    </div>

    <div class="quick-actions">
      <a href="#/feed" class="quick-action"><div class="ic">🧭</div><div class="t">Find a Skill Fit</div></a>
      <a href="#/deadlines" class="quick-action"><div class="ic">⏰</div><div class="t">Deadline Alerts</div></a>
      <a href="#/post" class="quick-action"><div class="ic">➕</div><div class="t">Post Opportunity</div></a>
      <a href="#/applications" class="quick-action"><div class="ic">📋</div><div class="t">My Applications</div></a>
      <a href="#/bookmarks" class="quick-action"><div class="ic">🔖</div><div class="t">Saved</div></a>
    </div>

    <div class="two-col">
      <div>
        <div class="section-title">Top Matches For You <a href="#/feed" class="text-sm">See all →</a></div>
        <div id="topMatches">
          ${topMatches.length === 0
            ? emptyState("🔍", "No matches yet", "Add more skills to your profile to discover opportunities.", `<a href="#/profile/edit" class="btn btn-primary btn-sm">Edit Profile</a>`)
            : `<div class="flex-col gap-14">${topMatches.map((o) => oppCardHtml(o)).join("")}</div>`
          }
        </div>
      </div>
      <div>
        <div class="section-title">Recent Applications</div>
        <div id="recentApps">
          ${applications.length === 0
            ? emptyState("📋", "No applications yet", "Apply to an opportunity to see it tracked here.")
            : applications.slice(0, 5).map((a) => `
              <div class="list-row">
                <div class="grow">
                  <div class="title">${escapeHtml(a.opportunity.title)}</div>
                  <div class="sub">${escapeHtml(a.opportunity.organization)} · ${timeAgo(a.applied_at)}</div>
                </div>
                ${statusBadge(a.status)}
              </div>
            `).join("")
          }
        </div>
      </div>
    </div>
  `;

  wireBookmarkButtons(root);
}
