async function renderFeed(root, _param, presetFilters = {}) {
  root.innerHTML = `
    <div class="filters-bar">
      <div class="field grow">
        <label>Search</label>
        <input type="text" id="fSearch" placeholder="Search title or description..." value="${escapeHtml(presetFilters.q || "")}" />
      </div>
      <div class="field">
        <label>Type</label>
        <select id="fType">
          <option value="">All Types</option>
          <option value="internship">Internship</option>
          <option value="project">Project</option>
          <option value="hackathon">Hackathon</option>
          <option value="freelance">Freelance</option>
        </select>
      </div>
      <div class="field">
        <label>Skill</label>
        <input type="text" id="fSkill" placeholder="e.g. Python" />
      </div>
      <div class="field">
        <label>City</label>
        <input type="text" id="fCity" placeholder="e.g. Chennai" />
      </div>
      <div class="field">
        <label>Mode</label>
        <select id="fMode">
          <option value="">Any Mode</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
          <option value="hybrid">Hybrid</option>
        </select>
      </div>
      <div class="field">
        <label>Paid</label>
        <select id="fPaid">
          <option value="">Any</option>
          <option value="true">Paid Only</option>
          <option value="false">Unpaid Only</option>
        </select>
      </div>
      <div class="field">
        <label>Sort By</label>
        <select id="fSort">
          <option value="match">Best Match</option>
          <option value="deadline">Deadline Soonest</option>
          <option value="newest">Newest First</option>
        </select>
      </div>
      <button class="btn btn-primary" id="applyFilters">Apply Filters</button>
    </div>
    <div id="feedResults">${loadingRow("Finding your matches...")}</div>
  `;

  if (presetFilters.type) root.querySelector("#fType").value = presetFilters.type;

  async function loadFeed() {
    const params = new URLSearchParams();
    const q = root.querySelector("#fSearch").value.trim();
    const type = root.querySelector("#fType").value;
    const skill = root.querySelector("#fSkill").value.trim();
    const city = root.querySelector("#fCity").value.trim();
    const mode = root.querySelector("#fMode").value;
    const paid = root.querySelector("#fPaid").value;
    const sort = root.querySelector("#fSort").value;

    if (q) params.set("q", q);
    if (type) params.set("type", type);
    if (skill) params.set("skill", skill);
    if (city) params.set("city", city);
    if (mode) params.set("mode", mode);
    if (paid) params.set("paid", paid);
    params.set("sort", sort);

    const resultsEl = root.querySelector("#feedResults");
    resultsEl.innerHTML = loadingRow("Searching...");

    try {
      const results = await api(`/opportunities/feed?${params.toString()}`);
      if (results.length === 0) {
        resultsEl.innerHTML = emptyState(
          "🔍",
          "No opportunities found",
          skill
            ? `No students... wait, no opportunities currently need "${skill}". Try another skill, or check back later.`
            : "Try adjusting your filters, or check back soon for new postings."
        );
        return;
      }
      resultsEl.innerHTML = `<div class="opp-grid">${results.map((o) => oppCardHtml(o, { showReasons: true })).join("")}</div>`;
      wireBookmarkButtons(resultsEl);
    } catch (err) {
      resultsEl.innerHTML = emptyState("⚠️", "Couldn't load the feed", err.message);
    }
  }

  root.querySelector("#applyFilters").addEventListener("click", loadFeed);
  ["fSearch", "fSkill", "fCity"].forEach((id) => {
    root.querySelector("#" + id).addEventListener("keydown", (e) => {
      if (e.key === "Enter") loadFeed();
    });
  });

  loadFeed();
}
