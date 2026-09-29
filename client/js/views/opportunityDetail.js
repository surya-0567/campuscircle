async function renderOpportunityDetail(root, id) {
  const user = getCachedUser();
  let opp;
  try {
    opp = await api(`/opportunities/${id}`);
  } catch (err) {
    root.innerHTML = emptyState("⚠️", "Opportunity not found", err.message, `<a href="#/feed" class="btn btn-primary btn-sm">Back to Feed</a>`);
    return;
  }

  const isOwner = opp.poster.id === user.id;

  root.innerHTML = `
    <div class="detail-grid">
      <div>
        <div class="detail-hero">
          <div class="flex justify-between items-center" style="flex-wrap:wrap; gap:10px;">
            <div>
              <h2>${escapeHtml(opp.title)} ${opp.is_referral ? '<span class="badge badge-referral">Alumni Referral</span>' : ""}</h2>
              <div class="org-line">${escapeHtml(opp.organization)} · ${escapeHtml(opp.city)} ${statusBadge(opp.status)}</div>
            </div>
            ${opp.is_closing_soon ? '<span class="badge badge-urgent">⏰ Closing Soon</span>' : ""}
          </div>

          ${oppMetaRow(opp)}

          <div class="detail-section">
            <h4>Description</h4>
            <p>${escapeHtml(opp.description) || "<span class='text-muted'>No description provided.</span>"}</p>
          </div>

          <div class="detail-section">
            <h4>Skills Required</h4>
            ${skillChips(opp.skills_required)}
          </div>

          <div class="info-grid">
            <div class="kv"><div class="k">Duration</div><div class="v">${escapeHtml(opp.duration) || "Not specified"}</div></div>
            <div class="kv"><div class="k">Eligibility</div><div class="v">${escapeHtml(opp.eligibility) || "Open to all"}</div></div>
            <div class="kv"><div class="k">Deadline</div><div class="v">${formatDeadline(opp.deadline)}</div></div>
            <div class="kv"><div class="k">Posted By</div><div class="v">${escapeHtml(opp.poster.name)} (${opp.poster.role})</div></div>
          </div>

          ${opp.external_link ? `<div class="detail-section"><a href="${escapeHtml(opp.external_link)}" target="_blank" class="btn btn-outline btn-sm">🔗 External Link</a></div>` : ""}
        </div>
      </div>

      <div class="flex-col gap-14">
        <div class="match-score-card">
          <div class="big-pct">${opp.match_score}%</div>
          <div class="text-muted text-sm">Match Score</div>
          ${opp.match_reasons && opp.match_reasons.length ? `
            <div class="match-reasons mt-14" style="text-align:left;"><ul>${opp.match_reasons.map((r) => `<li>${escapeHtml(r)}</li>`).join("")}</ul></div>
          ` : ""}
        </div>

        <div class="card">
          ${isOwner ? `
            <p class="text-sm text-muted mb-14">This is your posting.</p>
            <a href="#/my-postings" class="btn btn-outline btn-block mb-8">Manage / View Applicants</a>
          ` : opp.has_applied ? `
            <button class="btn btn-success btn-block" disabled>✅ Already Applied</button>
          ` : opp.status !== "open" ? `
            <button class="btn btn-ghost btn-block" disabled>This opportunity is closed</button>
          ` : `
            <button class="btn btn-primary btn-block" id="applyBtn">Apply Now</button>
          `}
          <button class="btn btn-ghost btn-block mt-8 bookmark-btn" data-id="${opp.id}" data-active="${opp.is_bookmarked}">
            ${opp.is_bookmarked ? "★ Saved" : "☆ Save for Later"}
          </button>
        </div>
      </div>
    </div>
  `;

  wireBookmarkButtons(root, () => renderOpportunityDetail(root, id));

  const applyBtn = root.querySelector("#applyBtn");
  if (applyBtn) {
    applyBtn.addEventListener("click", () => {
      const backdrop = modal(`
        <h3>Apply to ${escapeHtml(opp.title)}</h3>
        <p class="modal-sub">A short note helps the poster know why you're a good fit (optional).</p>
        <div class="field">
          <label>Cover Note</label>
          <textarea id="coverNote" rows="4" placeholder="I'm excited about this because..."></textarea>
        </div>
        <div class="modal-actions">
          <button class="btn btn-ghost" id="cancelApply">Cancel</button>
          <button class="btn btn-primary" id="confirmApply">Send Application</button>
        </div>
      `);
      backdrop.querySelector("#cancelApply").addEventListener("click", () => backdrop.remove());
      backdrop.querySelector("#confirmApply").addEventListener("click", async () => {
        const coverNote = backdrop.querySelector("#coverNote").value.trim();
        try {
          await api(`/applications/${opp.id}`, { method: "POST", body: { cover_note: coverNote } });
          toast("Application sent successfully!", "success");
          backdrop.remove();
          renderOpportunityDetail(root, id);
        } catch (err) {
          toast(err.message, "error");
        }
      });
    });
  }
}
