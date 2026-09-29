async function renderProfile(root) {
  const user = getCachedUser();
  let apps = [], postings = [];
  try {
    [apps, postings] = await Promise.all([api("/applications/mine"), api("/opportunities/mine")]);
  } catch (err) {
    // non-fatal - still show profile basics
  }

  root.innerHTML = `
    <div class="two-col">
      <div class="card">
        <div class="flex items-center gap-14 mb-20">
          <div class="avatar avatar-lg">${initials(user.name)}</div>
          <div>
            <div style="font-size:19px; font-weight:800;">${escapeHtml(user.name)}</div>
            <div class="text-muted text-sm">${escapeHtml(user.email)}</div>
            <span class="role-pill" style="background:var(--primary-soft); color:var(--primary); display:inline-block; margin-top:6px;">${user.role}</span>
          </div>
          <a href="#/profile/edit" class="btn btn-outline btn-sm" style="margin-left:auto;">Edit Profile</a>
        </div>

        ${user.bio ? `<p class="text-sm mb-20">${escapeHtml(user.bio)}</p>` : ""}

        <div class="info-grid mb-20">
          <div class="kv"><div class="k">College</div><div class="v">${escapeHtml(user.college) || "—"}</div></div>
          <div class="kv"><div class="k">City</div><div class="v">${escapeHtml(user.city) || "—"}</div></div>
          ${user.role === "student" ? `
            <div class="kv"><div class="k">Branch</div><div class="v">${escapeHtml(user.branch) || "—"}</div></div>
            <div class="kv"><div class="k">Year</div><div class="v">${user.year ? "Year " + user.year : "—"}</div></div>
          ` : `
            <div class="kv"><div class="k">Current Company</div><div class="v">${escapeHtml(user.current_company) || "—"}</div></div>
          `}
        </div>

        <div class="detail-section">
          <h4>Skills</h4>
          ${skillChips(user.skills)}
        </div>
        ${user.preferred_types && user.preferred_types.length ? `
          <div class="detail-section">
            <h4>Interested In</h4>
            <div class="chip-list">${user.preferred_types.map((t) => `<span class="badge badge-type">${TYPE_ICONS[t] || ""} ${TYPE_LABELS[t] || t}</span>`).join("")}</div>
          </div>
        ` : ""}
      </div>

      <div class="flex-col gap-14">
        <div class="stat-card"><div class="v">${apps.length}</div><div class="l">Applications Sent</div></div>
        <div class="stat-card"><div class="v">${postings.length}</div><div class="l">Opportunities Posted</div></div>
        <div class="stat-card"><div class="v">${apps.filter((a) => a.status === "selected").length}</div><div class="l">Selected</div></div>
      </div>
    </div>
  `;
}
