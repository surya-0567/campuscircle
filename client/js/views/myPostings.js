async function renderMyPostings(root) {
  let postings;
  try {
    postings = await api("/opportunities/mine");
  } catch (err) {
    root.innerHTML = emptyState("⚠️", "Couldn't load your postings", err.message);
    return;
  }

  if (postings.length === 0) {
    root.innerHTML = emptyState(
      "📦", "You haven't posted anything yet",
      "Share an internship, project, hackathon, or freelance gig with fellow students.",
      `<a href="#/post" class="btn btn-primary btn-sm">Post Your First Opportunity</a>`
    );
    return;
  }

  root.innerHTML = postings.map((o) => `
    <div class="card mb-14">
      <div class="flex justify-between items-center" style="flex-wrap:wrap; gap:10px;">
        <div>
          <div class="title" style="font-weight:700; font-size:15.5px;">${escapeHtml(o.title)} ${o.is_referral ? '<span class="badge badge-referral">Referral</span>' : ""}</div>
          <div class="text-sm text-muted">${escapeHtml(o.organization)} · ${o.application_count} applicant(s) · Deadline: ${formatDeadline(o.deadline)}</div>
        </div>
        <div class="flex gap-8 items-center">
          ${statusBadge(o.status)}
          <button class="btn btn-sm btn-outline toggle-applicants" data-id="${o.id}">View Applicants</button>
          <button class="btn btn-sm ${o.status === "open" ? "btn-danger" : "btn-success"} toggle-status" data-id="${o.id}" data-status="${o.status}">
            ${o.status === "open" ? "Close" : "Reopen"}
          </button>
          <button class="btn btn-sm btn-ghost delete-posting" data-id="${o.id}">Delete</button>
        </div>
      </div>
      <div class="mt-14 hidden" id="applicants-${o.id}"></div>
    </div>
  `).join("");

  root.querySelectorAll(".toggle-applicants").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      const container = root.querySelector(`#applicants-${id}`);
      if (!container.classList.contains("hidden")) {
        container.classList.add("hidden");
        btn.textContent = "View Applicants";
        return;
      }
      container.classList.remove("hidden");
      btn.textContent = "Hide Applicants";
      container.innerHTML = loadingRow("Loading applicants...");
      try {
        const applicants = await api(`/opportunities/${id}/applicants`);
        if (applicants.length === 0) {
          container.innerHTML = `<p class="text-sm text-muted">No applications yet.</p>`;
          return;
        }
        container.innerHTML = applicants.map((a) => `
          <div class="list-row">
            <div class="avatar avatar-sm">${initials(a.student.name)}</div>
            <div class="grow">
              <div class="title">${escapeHtml(a.student.name)} ${a.student.year ? `· Year ${a.student.year}` : ""}</div>
              <div class="sub">${escapeHtml(a.student.college || "")} ${a.student.branch ? "· " + escapeHtml(a.student.branch) : ""}</div>
              ${a.cover_note ? `<div class="text-sm mt-8" style="font-style:italic;">"${escapeHtml(a.cover_note)}"</div>` : ""}
              ${a.student.skills && a.student.skills.length ? `<div class="mt-8">${skillChips(a.student.skills)}</div>` : ""}
            </div>
            <div class="flex-col gap-8" style="align-items:flex-end;">
              ${statusBadge(a.status)}
              <select class="status-select" data-app-id="${a.id}" style="font-size:12px; padding:4px 8px;">
                <option value="applied" ${a.status === "applied" ? "selected" : ""}>Applied</option>
                <option value="shortlisted" ${a.status === "shortlisted" ? "selected" : ""}>Shortlisted</option>
                <option value="selected" ${a.status === "selected" ? "selected" : ""}>Selected</option>
                <option value="rejected" ${a.status === "rejected" ? "selected" : ""}>Not Selected</option>
              </select>
            </div>
          </div>
        `).join("");

        container.querySelectorAll(".status-select").forEach((sel) => {
          sel.addEventListener("change", async () => {
            try {
              await api(`/applications/${sel.dataset.appId}/status`, { method: "PATCH", body: { status: sel.value } });
              toast("Applicant status updated.", "success");
            } catch (err) {
              toast(err.message, "error");
            }
          });
        });
      } catch (err) {
        container.innerHTML = emptyState("⚠️", "Couldn't load applicants", err.message);
      }
    });
  });

  root.querySelectorAll(".toggle-status").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const newStatus = btn.dataset.status === "open" ? "closed" : "open";
      try {
        await api(`/opportunities/${btn.dataset.id}`, { method: "PATCH", body: { status: newStatus } });
        toast(`Opportunity ${newStatus === "closed" ? "closed" : "reopened"}.`, "success");
        renderMyPostings(root);
      } catch (err) {
        toast(err.message, "error");
      }
    });
  });

  root.querySelectorAll(".delete-posting").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this posting permanently? This can't be undone.")) return;
      try {
        await api(`/opportunities/${btn.dataset.id}`, { method: "DELETE" });
        toast("Posting deleted.", "info");
        renderMyPostings(root);
      } catch (err) {
        toast(err.message, "error");
      }
    });
  });
}
