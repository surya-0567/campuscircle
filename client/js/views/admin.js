async function renderAdmin(root) {
  const user = getCachedUser();
  if (user.role !== "admin") {
    root.innerHTML = emptyState("🔒", "Admins only", "You don't have access to this page.");
    return;
  }

  let stats;
  try {
    stats = await api("/admin/stats");
  } catch (err) {
    root.innerHTML = emptyState("⚠️", "Couldn't load admin stats", err.message);
    return;
  }

  root.innerHTML = `
    <div class="admin-stat-grid">
      <div class="admin-stat-card"><div class="v">${stats.totalStudents}</div><div class="l">Students</div></div>
      <div class="admin-stat-card"><div class="v">${stats.totalAlumni}</div><div class="l">Alumni</div></div>
      <div class="admin-stat-card"><div class="v">${stats.openOpportunities}</div><div class="l">Open Opportunities</div></div>
      <div class="admin-stat-card"><div class="v">${stats.totalApplications}</div><div class="l">Total Applications</div></div>
    </div>

    <div class="two-col">
      <div class="card">
        <div class="section-title">Popular Skills in Demand</div>
        ${stats.popularSkills.length === 0 ? `<p class="text-sm text-muted">No data yet.</p>` : `
          <table class="mini-table">
            <thead><tr><th>Skill</th><th>Postings</th></tr></thead>
            <tbody>${stats.popularSkills.map((s) => `<tr><td>${escapeHtml(s.skill)}</td><td>${s.count}</td></tr>`).join("")}</tbody>
          </table>
        `}
      </div>
      <div class="card">
        <div class="section-title">Opportunities by Type</div>
        <table class="mini-table">
          <thead><tr><th>Type</th><th>Count</th></tr></thead>
          <tbody>${stats.byType.map((t) => `<tr><td>${TYPE_ICONS[t.type] || ""} ${TYPE_LABELS[t.type] || t.type}</td><td>${t.count}</td></tr>`).join("")}</tbody>
        </table>
        <p class="text-sm text-muted mt-14">🎓 ${stats.totalReferrals} alumni referral(s) posted so far.</p>
      </div>
    </div>

    <div class="card mt-20">
      <div class="section-title">Recent Users <button class="btn btn-sm btn-outline" id="loadUsersBtn">Load</button></div>
      <div id="usersTable"></div>
    </div>
  `;

  root.querySelector("#loadUsersBtn").addEventListener("click", async () => {
    const container = root.querySelector("#usersTable");
    container.innerHTML = loadingRow("Loading users...");
    try {
      const users = await api("/admin/users");
      container.innerHTML = `
        <table class="mini-table">
          <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>College</th></tr></thead>
          <tbody>${users.slice(0, 50).map((u) => `
            <tr><td>${escapeHtml(u.name)}</td><td>${escapeHtml(u.email)}</td><td style="text-transform:capitalize;">${u.role}</td><td>${escapeHtml(u.college)}</td></tr>
          `).join("")}</tbody>
        </table>
      `;
    } catch (err) {
      container.innerHTML = emptyState("⚠️", "Couldn't load users", err.message);
    }
  });
}
