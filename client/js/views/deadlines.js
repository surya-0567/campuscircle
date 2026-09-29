async function renderDeadlines(root) {
  let results;
  try {
    results = await api("/opportunities/feed?closing_soon=true&sort=deadline");
  } catch (err) {
    root.innerHTML = emptyState("⚠️", "Couldn't load deadline alerts", err.message);
    return;
  }

  if (results.length === 0) {
    root.innerHTML = emptyState(
      "⏰", "Nothing closing soon",
      "You're all caught up! Opportunities closing within 3 days will show up here.",
      `<a href="#/feed" class="btn btn-primary btn-sm">Browse Full Feed</a>`
    );
    return;
  }

  root.innerHTML = `
    <div class="form-error show mb-20" style="background:#fff3e0; color:#b8541a;">
      ⏰ ${results.length} opportunity(s) matching your skills are closing within 3 days - don't miss out!
    </div>
    <div class="opp-grid">${results.map((o) => oppCardHtml(o, { showReasons: true })).join("")}</div>
  `;
  wireBookmarkButtons(root);
}
