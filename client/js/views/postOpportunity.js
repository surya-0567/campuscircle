async function renderPostOpportunity(root) {
  const user = getCachedUser();
  const isAlumni = user.role === "alumni" || user.role === "admin";
  const todayStr = new Date().toISOString().slice(0, 10);

  root.innerHTML = `
    <div class="card" style="max-width: 700px;">
      <div class="form-error" id="formError"></div>
      <form id="postForm">
        <div class="field">
          <label>Title</label>
          <input type="text" id="title" placeholder="e.g. Frontend Developer Intern" required />
        </div>

        <div class="field-row">
          <div class="field">
            <label>Type</label>
            <select id="type" required>
              <option value="internship">Internship</option>
              <option value="project">Project (need teammates)</option>
              <option value="hackathon">Hackathon</option>
              <option value="freelance">Freelance Gig</option>
            </select>
          </div>
          <div class="field">
            <label>Mode</label>
            <select id="mode">
              <option value="online">Online</option>
              <option value="offline">Offline</option>
              <option value="hybrid">Hybrid</option>
            </select>
          </div>
        </div>

        <div class="field">
          <label>Description</label>
          <textarea id="description" rows="4" placeholder="What's this opportunity about?"></textarea>
        </div>

        <div class="field">
          <label>Skills Required</label>
          <div class="tag-input-box" id="skillsBox">
            <input type="text" id="skillsInput" placeholder="Type a skill and press Enter" />
          </div>
        </div>

        <div class="field-row">
          <div class="field">
            <label>Organization</label>
            <input type="text" id="organization" placeholder="e.g. ${escapeHtml(user.college || user.current_company || "Your college/company")}" />
          </div>
          <div class="field">
            <label>City</label>
            <input type="text" id="city" placeholder="e.g. ${escapeHtml(user.city || "Chennai")}" />
          </div>
        </div>

        <div class="field-row">
          <div class="field">
            <label>Duration</label>
            <input type="text" id="duration" placeholder="e.g. 3 months / 24 hours" />
          </div>
          <div class="field">
            <label>Application Deadline</label>
            <input type="date" id="deadline" min="${todayStr}" required />
          </div>
        </div>

        <div class="field">
          <label>Eligibility</label>
          <input type="text" id="eligibility" placeholder="e.g. 2nd/3rd year, CSE/IT (leave blank if open to all)" />
        </div>

        <div class="field-row">
          <div class="field">
            <div class="checkbox-row"><input type="checkbox" id="paid" /> <label for="paid" style="margin:0;">This is paid</label></div>
          </div>
          <div class="field">
            <label>Stipend / Pay (if paid)</label>
            <input type="text" id="stipend" placeholder="e.g. ₹10,000/month" />
          </div>
        </div>

        <div class="field">
          <label>External Link (optional)</label>
          <input type="text" id="externalLink" placeholder="https://..." />
        </div>

        ${isAlumni ? `
          <div class="field">
            <div class="checkbox-row"><input type="checkbox" id="isReferral" /> <label for="isReferral" style="margin:0;">Mark this as an alumni referral</label></div>
            <div class="field-hint">Referrals are highlighted specially in the feed to help juniors from your college.</div>
          </div>
        ` : ""}

        <button type="submit" class="btn btn-primary btn-block" id="postBtn">Post Opportunity</button>
      </form>
    </div>
  `;

  // Skill tag input
  const skillsBox = root.querySelector("#skillsBox");
  const skillsInput = root.querySelector("#skillsInput");
  const skillTags = [];
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

  root.querySelector("#postForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errBox = root.querySelector("#formError");
    errBox.classList.remove("show");
    const btn = root.querySelector("#postBtn");
    btn.disabled = true;
    btn.textContent = "Posting...";

    try {
      const body = {
        title: root.querySelector("#title").value.trim(),
        type: root.querySelector("#type").value,
        mode: root.querySelector("#mode").value,
        description: root.querySelector("#description").value.trim(),
        skills_required: skillTags,
        organization: root.querySelector("#organization").value.trim(),
        city: root.querySelector("#city").value.trim(),
        duration: root.querySelector("#duration").value.trim(),
        deadline: root.querySelector("#deadline").value,
        eligibility: root.querySelector("#eligibility").value.trim(),
        paid: root.querySelector("#paid").checked,
        stipend: root.querySelector("#stipend").value.trim(),
        external_link: root.querySelector("#externalLink").value.trim(),
        is_referral: isAlumni ? !!root.querySelector("#isReferral")?.checked : false,
      };
      const created = await api("/opportunities", { method: "POST", body });
      toast("Opportunity posted successfully!", "success");
      window.location.hash = `#/opportunity/${created.id}`;
    } catch (err) {
      errBox.textContent = err.message;
      errBox.classList.add("show");
      btn.disabled = false;
      btn.textContent = "Post Opportunity";
    }
  });
}
