async function renderBookmarks(root) {
  let bookmarks;
  try {
    bookmarks = await api("/bookmarks");
  } catch (err) {
    root.innerHTML = emptyState("⚠️", "Couldn't load your bookmarks", err.message);
    return;
  }

  if (bookmarks.length === 0) {
    root.innerHTML = emptyState(
      "🔖", "Nothing saved yet",
      "Bookmark opportunities you're interested in to find them here later.",
      `<a href="#/feed" class="btn btn-primary btn-sm">Browse Opportunities</a>`
    );
    return;
  }

  root.innerHTML = `<div class="opp-grid">${bookmarks.map((b) => oppCardHtml(b.opportunity)).join("")}</div>`;
  wireBookmarkButtons(root, () => renderBookmarks(root));
}
