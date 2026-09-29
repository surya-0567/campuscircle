// Simple hash-based router. Each route maps to a render function that
// receives the #page-root element (and any params parsed from the hash).

const ROUTES = {
  dashboard: { title: "Dashboard", sub: "Your opportunities at a glance", render: renderDashboard },
  feed: { title: "Opportunity Feed", sub: "Internships, projects, hackathons & freelance gigs", render: renderFeed },
  deadlines: { title: "Deadline Alerts", sub: "Opportunities closing soon", render: renderDeadlines },
  bookmarks: { title: "Saved Opportunities", sub: "Your bookmarked opportunities", render: renderBookmarks },
  applications: { title: "My Applications", sub: "Track the status of everything you've applied to", render: renderMyApplications },
  post: { title: "Post an Opportunity", sub: "Share an internship, project, hackathon or gig", render: renderPostOpportunity },
  "my-postings": { title: "My Postings", sub: "Manage opportunities you've posted", render: renderMyPostings },
  profile: { title: "My Profile", sub: "", render: renderProfile },
  "profile/edit": { title: "Edit Profile", sub: "Update your skills and details", render: renderProfileEdit },
  settings: { title: "Settings", sub: "Account preferences", render: renderSettings },
  admin: { title: "Admin", sub: "College-level oversight", render: renderAdmin },
};

function parseHash() {
  const hash = window.location.hash.replace(/^#\//, "");
  const parts = hash.split("/").filter(Boolean);
  return parts;
}

async function router() {
  const parts = parseHash();
  const pageRoot = document.getElementById("page-root");
  let routeKey = parts[0] || "dashboard";
  let param = parts[1];

  // Special two-segment routes
  if (routeKey === "opportunity" && param) {
    setActiveNav("feed");
    document.getElementById("topbarTitle").textContent = "Opportunity Details";
    document.getElementById("topbarSub").textContent = "";
    pageRoot.innerHTML = loadingRow();
    return renderOpportunityDetail(pageRoot, param);
  }
  if (routeKey === "profile" && param === "edit") {
    routeKey = "profile/edit";
  }

  const route = ROUTES[routeKey] || ROUTES.dashboard;
  setActiveNav(routeKey.split("/")[0]);
  document.getElementById("topbarTitle").textContent = route.title;
  document.getElementById("topbarSub").textContent = route.sub || "";
  pageRoot.innerHTML = loadingRow();

  try {
    await route.render(pageRoot, param);
  } catch (err) {
    pageRoot.innerHTML = emptyState("⚠️", "Something went wrong", err.message);
  }
}

function setActiveNav(routeKey) {
  document.querySelectorAll(".nav-link").forEach((a) => {
    a.classList.toggle("active", a.dataset.route === routeKey);
  });
}

function renderSidebarUser() {
  const user = getCachedUser();
  if (!user) return;
  document.getElementById("sidebarAvatar").textContent = initials(user.name);
  document.getElementById("sidebarName").textContent = user.name;
  document.getElementById("sidebarEmail").textContent = user.email;
  document.getElementById("sidebarRole").textContent = user.role;
  if (user.role === "admin") {
    document.getElementById("adminLink").classList.remove("hidden");
  }
}

async function refreshCachedUser() {
  const data = await api("/auth/me");
  const token = getToken();
  setSession(token, data);
  renderSidebarUser();
  return data;
}

document.getElementById("logoutBtn").addEventListener("click", () => {
  clearSession();
  window.location.href = "/login";
});

document.getElementById("menuBtn").addEventListener("click", () => {
  document.getElementById("sidebar").classList.toggle("open");
});

window.addEventListener("hashchange", router);
