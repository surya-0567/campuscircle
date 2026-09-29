async function renderProfileEdit(root) {
  const user = getCachedUser();
  const isStudent = user.role === "student";

  root.innerHTML = `
    <div class="card" style="max-width: 640px;">
      <div class="form-error" id="formError"></div>
      <form id="editForm">
        <div class="field">
          <label>Full Name</label>
          <input type="text" id="name" value="${escapeHtml(user.name)}" required />
        </div>
        <div class="field">
          <label>Bio</label>
          <textarea id="bio" rows="3">${escapeHtml(user.bio)}</textarea>
        </div>
        <div class="field-row">
          <div class="field">
            <label>College</label>
            <input type="text" id="college" value="${escapeHtml(user.college)}" />
          </div>
          <div class="field">
            <label>City</label>
            <input type="text" id="city" value="${escapeHtml(user.city)}" />
          </div>
        </div>
        ${isStudent ? `
          <div class="field-row">
            <div class="field">
              <label>Branch</label>
              <input type="text" id="branch" value="${escapeHtml(user.branch)}" />
            </div>
            <div class="field">
              <label>Year</label>
              <select id="year">
                <option value="">Select year</option>
                <option value="1" ${user.year === 1 ? "selected" : ""}>1st Year</option>
                <option value="2" ${user.year === 2 ? "selected" : ""}>2nd Year</option>
                <option value="3" ${user.year === 3 ? "selected" : ""}>3rd Year</option>
                <option value="4" ${user.year === 4 ? "selected" : ""}>4th Year</option>
              </select>
            </div>
          </div>
        ` : `
          <div class="field">
            <label>Current Company</label>
            <input type="text" id="currentCompany" value="${escapeHtml(user.current_company)}" />
          </div>
        `}

        <div class="field">
          <label>Skills</label>
          <div class="tag-input-box" id="skillsBox">
            <input type="text" id="skillsInput" placeholder="Type a skill and press Enter" />
          </div>
        </div>

        <div class="field">
          <label>Interested Opportunity Types</label>
          <div class="chip-list" id="typeToggle">
            ${["internship", "project", "hackathon", "freelance"].map((t) => `
              <label class="chip" style="cursor:pointer;">
                <input type="checkbox" value="${t}" ${user.preferred_types.includes(t) ? "checked" : ""} style="margin-right:6px;" />
                ${TYPE_LABELS[t]}
              </label>
            `).join("")}
          </div>
        </div>

        <button type="submit" class="btn btn-primary btn-block" id="saveBtn">Save Changes</button>
      </form>
    </div>
  `;

  const skillsBox = root.querySelector("#skillsBox");
  const skillsInput = root.querySelector("#skillsInput");
  const skillTags = [...user.skills];
  function renderSkillChips() {
    skillsBox.querySelectorAll(".chip").forEach((c) => c.remove());
    skillTags.forEach((tag, i) => {
      const chip = document.createElement("span");
      chip.className = "chip chip-remove";
      chip.innerHTML = `${escapeHtml(tag)} <button type="button" data-i="${i}">&times;</button>`;
      skillsBox.insertBefore(chip, skillsInput);
    });
    skillsBox.querySelectorAll(".chip button").forEach((btn) => {
      btn.addEventListener("click", () => { skillTags.splice(Number(btn.dataset.i), 1); renderSkillChips(); });
    });
  }
  renderSkillChips();
  skillsInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      const v = skillsInput.value.trim();
      if (v && !skillTags.some((t) => t.toLowerCase() === v.toLowerCase())) {
        skillTags.push(v);
        renderSkillChips();
      }
      skillsInput.value = "";
    }
  });
  skillsBox.addEventListener("click", () => skillsInput.focus());

  root.querySelector("#editForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errBox = root.querySelector("#formError");
    errBox.classList.remove("show");
    const btn = root.querySelector("#saveBtn");
    btn.disabled = true;
    btn.textContent = "Saving...";

    const preferredTypes = Array.from(root.querySelectorAll('#typeToggle input:checked')).map((c) => c.value);

    try {
      const body = {
        name: root.querySelector("#name").value.trim(),
        bio: root.querySelector("#bio").value.trim(),
        college: root.querySelector("#college").value.trim(),
        city: root.querySelector("#city").value.trim(),
        skills: skillTags,
        preferred_types: preferredTypes,
      };
      if (isStudent) {
        body.branch = root.querySelector("#branch").value.trim();
        body.year = root.querySelector("#year").value ? Number(root.querySelector("#year").value) : null;
      } else {
        body.current_company = root.querySelector("#currentCompany").value.trim();
      }
      const updated = await api("/users/me", { method: "PUT", body });
      setSession(getToken(), updated);
      renderSidebarUser();
      toast("Profile updated!", "success");
      window.location.hash = "#/profile";
    } catch (err) {
      errBox.textContent = err.message;
      errBox.classList.add("show");
      btn.disabled = false;
      btn.textContent = "Save Changes";
    }
  });
}
