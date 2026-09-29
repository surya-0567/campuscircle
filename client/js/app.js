// Bootstraps the CampusCircle app shell: guards the route behind login,
// refreshes the cached user, then starts the hash router.
(async function bootstrap() {
  if (!getToken()) {
    window.location.href = "/login";
    return;
  }

  renderSidebarUser(); // paint immediately from cache, then refresh from server
  try {
    await refreshCachedUser();
  } catch (err) {
    // api() already redirects to /login on a real 401; anything else, just continue.
  }

  if (!window.location.hash) {
    window.location.hash = "#/dashboard";
  }
  router();
})();
