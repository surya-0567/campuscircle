async function renderSettings(root) {
  const user = getCachedUser();

  root.innerHTML = `
    <div class="card" style="max-width: 600px;">
      <div class="settings-section">
        <h3 class="section-title">Account Information</h3>
        <div class="info-grid">
          <div class="kv"><div class="k">Name</div><div class="v">${escapeHtml(user.name)}</div></div>
          <div class="kv"><div class="k">Email</div><div class="v">${escapeHtml(user.email)}</div></div>
          <div class="kv"><div class="k">Role</div><div class="v" style="text-transform:capitalize;">${user.role}</div></div>
          <div class="kv"><div class="k">Member Since</div><div class="v">${new Date(user.created_at).toLocaleDateString()}</div></div>
        </div>
      </div>

      <div class="settings-section mt-20">
        <h3 class="section-title">Profile</h3>
        <p class="text-sm text-muted mb-14">Update your skills, bio, and other details from the Edit Profile page.</p>
        <a href="#/profile/edit" class="btn btn-outline">Edit Profile</a>
      </div>

      <div class="settings-section mt-20">
        <h3 class="section-title">Session</h3>
        <p class="text-sm text-muted mb-14">Log out of CampusCircle on this device.</p>
        <button class="btn btn-danger" id="settingsLogout">Log Out</button>
      </div>
    </div>
  `;

  root.querySelector("#settingsLogout").addEventListener("click", () => {
    clearSession();
    window.location.href = "/login";
  });
}
