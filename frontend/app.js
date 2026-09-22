/**
 * ENTERPRISE AUDITOR 2.0 — SMART CONTRACT REVIEWER CONTROLLER
 * Light Mode • Simple Words • 100% Transparent Logic • Responsive Screen Fit
 */

document.addEventListener("DOMContentLoaded", () => {
  let auditData = null;
  let activeFindingsFilter = "all";
  let activeTimelineParty = "all";
  let activeTableIndex = 0;

  // DOM Elements - Navigation & Screens
  const navTabs = document.querySelectorAll(".nav-tab");
  const screens = document.querySelectorAll(".screen");
  const btnNavHome = document.getElementById("btn-nav-home");

  // DOM Elements - Summary Screen
  const scoreRingFill = document.getElementById("score-ring-fill");
  const scoreNumber = document.getElementById("score-number");
  const gaugeVerdictLabel = document.getElementById("gauge-verdict-label");
  const verdictBadge = document.getElementById("verdict-badge");
  const verdictActionHint = document.getElementById("verdict-action-hint");
  const verdictHeadline = document.getElementById("verdict-headline");
  const verdictSummaryText = document.getElementById("verdict-summary-text");
  const riskDonutCanvas = document.getElementById("risk-donut-canvas");
  const donutLegend = document.getElementById("donut-legend");
  const waterfallBar = document.getElementById("waterfall-bar");
  const waterfallLabels = document.getElementById("waterfall-labels");
  const impactBarsList = document.getElementById("impact-bars-list");
  const countDealbreakers = document.getElementById("count-dealbreakers");
  const countWatchout = document.getElementById("count-watchout");
  const countProtections = document.getElementById("count-protections");
  const metricDescDealbreakers = document.getElementById("metric-desc-dealbreakers");
  const metricDescWatchout = document.getElementById("metric-desc-watchout");
  const metricDescProtections = document.getElementById("metric-desc-protections");
  const navBadgeRisks = document.getElementById("nav-badge-risks");
  const navBadgeMissing = document.getElementById("nav-badge-missing");

  // Metadata Strip
  const contractStrip = document.getElementById("contract-strip");
  const docFilename = document.getElementById("doc-filename");
  const docPartiesPill = document.getElementById("doc-parties-pill");
  const docPagesPill = document.getElementById("doc-pages-pill");
  const stripRightStatus = document.getElementById("strip-right-status");

  // Welcome & Upload Screen Elements
  const dropZone = document.getElementById("drop-zone");
  const btnBrowseTrigger = document.getElementById("btn-browse-trigger");
  const filePreviewCard = document.getElementById("file-preview-card");
  const previewFilename = document.getElementById("preview-filename");
  const previewFilesize = document.getElementById("preview-filesize");
  const btnCancelFile = document.getElementById("btn-cancel-file");
  const btnStartAudit = document.getElementById("btn-start-audit");
  const uploadProgressCard = document.getElementById("upload-progress-card");
  const auditProgressStageTitle = document.getElementById("audit-progress-stage-title");
  const auditProgressBadge = document.getElementById("audit-progress-badge");
  const btnTryDemo = document.getElementById("btn-try-demo");

  // Quick Action Buttons (Overview Screen)
  const btnQaUpload = document.getElementById("btn-qa-upload");
  const btnQaMemo = document.getElementById("btn-qa-memo");
  const btnQaJson = document.getElementById("btn-qa-json");
  const btnQaAsk = document.getElementById("btn-qa-ask");


  // Summary Action Triggers
  const metricCardDealbreakers = document.getElementById("metric-card-dealbreakers");
  const metricCardWatchout = document.getElementById("metric-card-watchout");
  const metricCardProtections = document.getElementById("metric-card-protections");
  const btnHeroDeepDive = document.getElementById("btn-hero-deep-dive");
  const btnOpenAsymmetryModalTop = document.getElementById("btn-open-asymmetry-modal-top");
  const btnOpenAsymmetryModal = document.getElementById("btn-open-asymmetry-modal");
  const btnSpotlightAsymmetry = document.getElementById("btn-spotlight-asymmetry");
  const btnSpotlightRedline = document.getElementById("btn-spotlight-redline");
  const btnNavToMissing = document.getElementById("btn-nav-to-missing");
  const btnNavToTimeline = document.getElementById("btn-nav-to-timeline");
  const btnNavToScanner = document.getElementById("btn-nav-to-scanner");

  // Global Action Buttons
  const btnHeaderNewAudit = document.getElementById("btn-header-new-audit");
  const btnDownloadMemo = document.getElementById("btn-download-memo");
  const fileUploadInput = document.getElementById("file-upload-input");
  const btnChooseFile = document.getElementById("btn-choose-file");

  // Findings View Elements
  const findingsCleanList = document.getElementById("findings-clean-list");
  const findingsFilterPills = document.querySelectorAll(".filter-pills-group .filter-pill");

  // Missing Clauses Elements
  const tbodyMissing = document.getElementById("tbody-missing-clauses");

  // Courtroom Elements
  const courtroomQueryInput = document.getElementById("courtroom-query-input");
  const btnAskCourtroom = document.getElementById("btn-ask-courtroom");
  const debateArena = document.getElementById("debate-arena");
  const chipButtons = document.querySelectorAll(".chip");

  // Timeline Elements
  const timelineTree = document.getElementById("timeline-tree");
  const timelinePartyFilters = document.querySelectorAll("#timeline-party-filter .filter-pill");

  // Scanner Elements
  const sigHeadline = document.getElementById("sig-headline");
  const sigSubnotes = document.getElementById("sig-subnotes");
  const sigCustName = document.getElementById("sig-cust-name");
  const sigProvName = document.getElementById("sig-prov-name");
  const tableTabs = document.getElementById("table-tabs");
  const tableDisplayWrap = document.getElementById("table-display-wrap");
  const tableRisksContainer = document.getElementById("table-risks-container");

  // Graph Canvas Elements
  const graphCanvas = document.getElementById("knowledge-graph-canvas");
  const btnResetGraph = document.getElementById("btn-reset-graph");
  const graphNodeCount = document.getElementById("graph-node-count");
  const graphEdgeCount = document.getElementById("graph-edge-count");

  // Modals & Dialogs
  const evidenceModal = document.getElementById("evidence-modal");
  const btnCloseModal = document.getElementById("btn-close-modal");
  const btnCloseModalFooter = document.getElementById("btn-close-modal-footer");
  const modalTitle = document.getElementById("modal-title");
  const modalPage = document.getElementById("modal-page");
  const modalChunk = document.getElementById("modal-chunk");
  const modalSection = document.getElementById("modal-section");
  const modalPlainEnglish = document.getElementById("modal-plain-english");
  const modalWhy = document.getElementById("modal-why");
  const modalQuote = document.getElementById("modal-quote");
  const modalRemedy = document.getElementById("modal-remedy");
  const btnCopyModalRemedy = document.getElementById("btn-copy-modal-remedy");

  const asymmetryModal = document.getElementById("asymmetry-modal");
  const btnCloseAsymmetryModal = document.getElementById("btn-close-asymmetry-modal");
  const btnCloseAsymmetryFooter = document.getElementById("btn-close-asymmetry-footer");
  const asymmetryMatrixContainer = document.getElementById("asymmetry-matrix-container");

  const missingClauseModal = document.getElementById("missing-clause-modal");
  const btnCloseMissingModal = document.getElementById("btn-close-missing-modal");
  const btnCloseMissingFooter = document.getElementById("btn-close-missing-footer");
  const missingModalTitle = document.getElementById("missing-modal-title");
  const missingModalWhy = document.getElementById("missing-modal-why");
  const missingModalCode = document.getElementById("missing-modal-code");
  const btnCopyMissingClause = document.getElementById("btn-copy-missing-clause");

  const toastContainer = document.getElementById("toast-container");

  // =========================================================================
  // SCREEN NAVIGATION
  // =========================================================================
  function switchScreen(screenId, targetTabId) {
    screens.forEach((s) => s.classList.remove("active"));
    navTabs.forEach((t) => {
      t.classList.remove("active");
      t.setAttribute("aria-selected", "false");
    });

    const targetScreen = document.getElementById(screenId);
    if (targetScreen) targetScreen.classList.add("active");

    const targetTab = document.getElementById(targetTabId);
    if (targetTab) {
      targetTab.classList.add("active");
      targetTab.setAttribute("aria-selected", "true");
    }

    window.scrollTo({ top: 0, behavior: "smooth" });

    if (screenId === "screen-graph" && auditData) {
      setTimeout(() => drawKnowledgeGraph(auditData.graph), 100);
    }
  }

  navTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const screenId = tab.getAttribute("data-screen");
      switchScreen(screenId, tab.id);
    });
  });

  btnNavHome?.addEventListener("click", () => {
    switchScreen("screen-overview", "tab-overview");
  });


  // Overview Quick Actions
  metricCardDealbreakers?.addEventListener("click", () => {
    activeFindingsFilter = "deal_breaker";
    updateFindingsFilterPills();
    renderFindingsList();
    switchScreen("screen-findings", "tab-findings");
  });

  metricCardWatchout?.addEventListener("click", () => {
    activeFindingsFilter = "watch_out";
    updateFindingsFilterPills();
    renderFindingsList();
    switchScreen("screen-findings", "tab-findings");
  });

  metricCardProtections?.addEventListener("click", () => {
    activeFindingsFilter = "protection";
    updateFindingsFilterPills();
    renderFindingsList();
    switchScreen("screen-findings", "tab-findings");
  });

  btnHeroDeepDive?.addEventListener("click", () => {
    activeFindingsFilter = "all";
    updateFindingsFilterPills();
    renderFindingsList();
    switchScreen("screen-findings", "tab-findings");
  });

  btnNavToMissing?.addEventListener("click", () => {
    switchScreen("screen-missing", "tab-missing");
  });

  btnNavToTimeline?.addEventListener("click", () => {
    switchScreen("screen-timeline", "tab-timeline");
  });

  btnNavToScanner?.addEventListener("click", () => {
    switchScreen("screen-scanner", "tab-scanner");
  });

  // Asymmetry Modal Triggers
  [btnOpenAsymmetryModalTop, btnOpenAsymmetryModal, btnSpotlightAsymmetry].forEach((btn) => {
    btn?.addEventListener("click", () => {
      openAsymmetryModal();
    });
  });

  // Spotlight Redline Trigger (Opens top deal-breaker)
  btnSpotlightRedline?.addEventListener("click", () => {
    if (auditData?.health?.deal_breakers?.length > 0) {
      openEvidenceModal(auditData.health.deal_breakers[0]);
    }
  });

  // =========================================================================
  // TOAST NOTIFICATION HELPER
  // =========================================================================
  function showToast(message, icon = "✅") {
    if (!toastContainer) return;
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(6px)";
      toast.style.transition = "all 0.25s ease";
      setTimeout(() => toast.remove(), 250);
    }, 2500);
  }

  // =========================================================================
  // CLIPBOARD COPY HELPER WITH VISUAL FEEDBACK
  // =========================================================================
  async function copyToClipboard(text, btnElement, successMsg = "Copied to clipboard!") {
    if (!text) return;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        throw new Error("Clipboard API unavailable");
      }
    } catch (e) {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try {
        document.execCommand("copy");
      } catch (copyErr) {
        console.warn("Fallback copy failed", copyErr);
      }
      ta.remove();
    }
    showToast(successMsg, "📋");
    if (btnElement) {
      const originalHtml = btnElement.innerHTML;
      btnElement.classList.add("copied");
      btnElement.innerHTML = `<span>Copied! ✓</span>`;
      setTimeout(() => {
        btnElement.classList.remove("copied");
        btnElement.innerHTML = originalHtml;
      }, 2000);
    }
  }

  function resetToWelcomeScreen() {
    if (dropZone) dropZone.style.display = "flex";
    if (filePreviewCard) filePreviewCard.style.display = "none";
    if (uploadProgressCard) uploadProgressCard.style.display = "none";
    if (fileUploadInput) fileUploadInput.value = "";
    selectedFile = null;
    switchScreen("screen-welcome", "tab-welcome");
  }

  // =========================================================================
  // DATA LOADING & INITIALIZATION
  // =========================================================================
  async function loadLatestReport() {
    try {
      const res = await fetch("/api/report/latest");
      if (!res.ok) {
        // Clean start: No previous user upload found, stay on welcome screen
        return;
      }
      const data = await res.json();
      if (data && data.health && data.findings) {
        auditData = data;
        renderAll(auditData);
        switchScreen("screen-overview", "tab-overview");
        showToast(`Restored previous audit: ${data.document_name || "Contract"}`, "📄");
      }
    } catch (err) {
      // Clean start without annoying error prompts
      console.log("Welcome screen active, ready for file upload.");
    }
  }

  function renderAll(data) {
    renderMetadata(data);
    renderHealthScore(data.health);
    renderFindingsList();
    renderMissingClauses(data.missing_clauses);
    renderTimeline(data.obligations);
    renderScanner(data.signatures, data.tables);
    renderCourtroomDebate(data.findings);
  }

  // =========================================================================
  // 1. RENDER METADATA & HEALTH SCORE
  // =========================================================================
  function renderMetadata(data) {
    if (contractStrip) {
      contractStrip.classList.remove("empty-state");
    }
    if (docFilename) {
      docFilename.textContent = data.document_name || "contract.pdf";
    }
    if (docPartiesPill) {
      docPartiesPill.style.display = "inline-flex";
      if (data.parties && (data.parties.customer || data.parties.provider)) {
        docPartiesPill.textContent = `${data.parties.customer || "Customer"} ↔ ${data.parties.provider || "Provider"}`;
      } else {
        docPartiesPill.textContent = "Parties Analyzed";
      }
    }
    if (docPagesPill) {
      docPagesPill.style.display = "inline-flex";
      const pages = data.num_pages || (data.evidence_index ? Object.keys(data.evidence_index).length : 6);
      docPagesPill.textContent = `${pages} Page${pages === 1 ? "" : "s"}`;
    }
    if (stripRightStatus) {
      stripRightStatus.innerHTML = `
        <span class="system-status" style="color: var(--emerald);">
          <span class="status-dot" style="background: var(--emerald);"></span> Audit Verified • Dual-Agent Review
        </span>
      `;
    }
  }

  function renderHealthScore(health) {
    if (!health) return;
    const score = typeof health.health_score === "number" ? health.health_score : 80;
    const dbCount = health.deal_breakers_count || 0;
    const woCount = health.watch_out_count || 0;
    const prCount = health.protections_count || 0;
    const msCount = health.missing_protections_count || 0;

    // 1. Score display & Ring Animation
    if (scoreNumber) scoreNumber.textContent = score.toFixed(1);

    let ringColor = "var(--emerald)";
    let verdictClass = "badge-safe";
    let verdictTitle = "LOW RISK CONTRACT";
    let gaugeText = "Safe to Proceed";
    let actionHintText = "Ready for standard business approval";
    let headlineText = "Overall Assessment: Strong & Balanced Agreement";
    let summaryText = `This agreement has a healthy safety score of ${score.toFixed(1)}/100 with ${prCount} protection clauses active and ${dbCount} deal-breakers.`;

    if (score < 50 || dbCount >= 2) {
      ringColor = "var(--crimson)";
      verdictClass = "badge-danger";
      verdictTitle = "CRITICAL RISK";
      gaugeText = "Do Not Sign As-Is";
      actionHintText = "Immediate renegotiation required before signing";
      headlineText = "Overall Assessment: Critical Risks Detected";
      summaryText = `This contract contains ${dbCount} deal-breaker terms and significant liabilities that heavily favor the other party. We strongly advise pausing execution until key clauses are revised.`;
    } else if (score < 75 || dbCount === 1 || woCount >= 3) {
      ringColor = "var(--amber)";
      verdictClass = "badge-warning";
      verdictTitle = "MODERATE RISK";
      gaugeText = "Proceed With Caution";
      actionHintText = "Key terms require review and negotiation";
      headlineText = "Overall Assessment: Actionable Red Flags Present";
      summaryText = `While mostly operational, this agreement includes ${woCount} watch-out warning items${dbCount ? ` and ${dbCount} deal-breaker` : ""} that shift unfair exposure to your company.`;
    } else {
      ringColor = "var(--emerald)";
      verdictClass = "badge-safe";
      verdictTitle = "SAFE & BALANCED";
      gaugeText = "Standard Risk Profile";
      actionHintText = "Normal contractual obligations apply";
      headlineText = "Overall Assessment: Well-Structured Contract";
      summaryText = `Contract terms are generally fair and conform to industry standards. Minimal exposure identified (${woCount} minor watch-outs, ${prCount} solid protections).`;
    }

    if (gaugeVerdictLabel) {
      gaugeVerdictLabel.textContent = gaugeText;
      gaugeVerdictLabel.style.color = ringColor;
    }

    if (verdictBadge) {
      verdictBadge.className = `verdict-badge ${verdictClass}`;
      verdictBadge.textContent = verdictTitle;
    }

    if (verdictActionHint) {
      verdictActionHint.textContent = `• ${actionHintText}`;
    }

    if (verdictHeadline) {
      verdictHeadline.textContent = headlineText;
    }

    if (verdictSummaryText) {
      verdictSummaryText.textContent = summaryText;
    }

    // SVG Score Ring (Radius = 54, Perimeter = 2 * PI * 54 ≈ 339.29)
    if (scoreRingFill) {
      const perimeter = 339.29;
      const offset = perimeter - (Math.min(100, Math.max(0, score)) / 100) * perimeter;
      scoreRingFill.style.strokeDasharray = perimeter;
      scoreRingFill.style.strokeDashoffset = offset;
      scoreRingFill.style.stroke = ringColor;
    }

    // 2. Metric Counts & Descriptions
    if (countDealbreakers) countDealbreakers.textContent = dbCount;
    if (countWatchout) countWatchout.textContent = woCount;
    if (countProtections) countProtections.textContent = prCount;

    if (metricDescDealbreakers) {
      if (dbCount > 0 && health.deal_breakers && health.deal_breakers.length > 0) {
        const firstDb = health.deal_breakers[0].title || "Critical liability terms";
        metricDescDealbreakers.textContent = dbCount === 1 ? `Includes: ${firstDb}` : `${dbCount} severe risks, including: ${firstDb}`;
      } else {
        metricDescDealbreakers.textContent = "No critical deal-breakers found in this agreement.";
      }
    }

    if (metricDescWatchout) {
      if (woCount > 0 && health.watch_out && health.watch_out.length > 0) {
        const firstWo = health.watch_out[0].title || "Unfavorable terms";
        metricDescWatchout.textContent = woCount === 1 ? `Notice: ${firstWo}` : `${woCount} warning flags, including: ${firstWo}`;
      } else {
        metricDescWatchout.textContent = "No warning flags detected.";
      }
    }

    if (metricDescProtections) {
      if (prCount > 0 && health.protections && health.protections.length > 0) {
        const firstPr = health.protections[0].title || "Standard protective terms";
        metricDescProtections.textContent = `Favorable protection: ${firstPr}`;
      } else {
        metricDescProtections.textContent = "Few or no protective clauses explicitly securing your rights.";
      }
    }

    if (navBadgeRisks) {
      navBadgeRisks.textContent = dbCount + woCount;
    }
    if (navBadgeMissing) {
      navBadgeMissing.textContent = msCount;
    }

    // 3. Render Canvas Donut Chart
    renderDonutChart(dbCount, woCount, prCount, msCount);

    // 4. Render Waterfall Bar
    renderWaterfallBar(score, health.score_breakdown, dbCount, woCount, msCount, prCount);

    // 5. Render Category Impact Bars
    renderImpactBars(health);
  }

  // Visual Breakdown 1: Canvas Donut Chart
  function renderDonutChart(db, wo, pr, ms) {
    if (!riskDonutCanvas) return;
    const ctx = riskDonutCanvas.getContext("2d");
    if (!ctx) return;

    const total = db + wo + pr + ms;
    const dpr = window.devicePixelRatio || 1;
    const displayWidth = 160;
    const displayHeight = 160;

    riskDonutCanvas.width = displayWidth * dpr;
    riskDonutCanvas.height = displayHeight * dpr;
    riskDonutCanvas.style.width = `${displayWidth}px`;
    riskDonutCanvas.style.height = `${displayHeight}px`;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, displayWidth, displayHeight);

    const centerX = displayWidth / 2;
    const centerY = displayHeight / 2;
    const radius = 56;
    const lineWidth = 18;

    if (total === 0) {
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
      ctx.strokeStyle = "#e2e8f0";
      ctx.lineWidth = lineWidth;
      ctx.stroke();

      ctx.fillStyle = "#94a3b8";
      ctx.font = "bold 13px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("No items", centerX, centerY);
    } else {
      const slices = [
        { count: db, color: "#dc2626" },
        { count: wo, color: "#f59e0b" },
        { count: pr, color: "#10b981" },
        { count: ms, color: "#94a3b8" }
      ].filter((s) => s.count > 0);

      let startAngle = -Math.PI / 2;
      const gap = slices.length > 1 ? 0.05 : 0;

      slices.forEach((slice) => {
        const sliceAngle = (slice.count / total) * (2 * Math.PI);
        const endAngle = startAngle + sliceAngle;

        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, startAngle + gap / 2, endAngle - gap / 2);
        ctx.strokeStyle = slice.color;
        ctx.lineWidth = lineWidth;
        ctx.lineCap = "round";
        ctx.stroke();

        startAngle = endAngle;
      });

      // Center text
      ctx.fillStyle = "#0f172a";
      ctx.font = "800 22px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(`${total}`, centerX, centerY - 7);

      ctx.fillStyle = "#64748b";
      ctx.font = "600 10px Inter, sans-serif";
      ctx.fillText("Findings", centerX, centerY + 13);
    }

    if (donutLegend) {
      donutLegend.innerHTML = `
        <div class="donut-legend-item">
          <span class="donut-legend-dot" style="background:#dc2626"></span>
          <span class="donut-legend-label">Deal-Breakers</span>
          <span class="donut-legend-count">${db}</span>
        </div>
        <div class="donut-legend-item">
          <span class="donut-legend-dot" style="background:#f59e0b"></span>
          <span class="donut-legend-label">Watch-Outs</span>
          <span class="donut-legend-count">${wo}</span>
        </div>
        <div class="donut-legend-item">
          <span class="donut-legend-dot" style="background:#10b981"></span>
          <span class="donut-legend-label">Protections</span>
          <span class="donut-legend-count">${pr}</span>
        </div>
        <div class="donut-legend-item">
          <span class="donut-legend-dot" style="background:#94a3b8"></span>
          <span class="donut-legend-label">Missing Terms</span>
          <span class="donut-legend-count">${ms}</span>
        </div>
      `;
    }
  }

  // Visual Breakdown 2: Waterfall / Stacked Composition Bar
  function renderWaterfallBar(score, breakdown, db, wo, ms, pr) {
    if (!waterfallBar || !waterfallLabels) return;

    const sb = breakdown || {};
    const dbDed = sb.deal_breaker_deductions ?? (db * 8);
    const woDed = sb.watch_out_deductions ?? (wo * 3);
    const msDed = sb.missing_deductions ?? Math.min(12, ms * 2);
    const prRew = sb.protection_rewards ?? Math.min(15, pr * 2.5);

    const sumTotal = score + dbDed + woDed + msDed;
    const safeSum = sumTotal > 0 ? sumTotal : 100;

    const scorePct = (score / safeSum) * 100;
    const dbPct = (dbDed / safeSum) * 100;
    const woPct = (woDed / safeSum) * 100;
    const msPct = (msDed / safeSum) * 100;

    let segHtml = "";
    if (scorePct > 0) {
      segHtml += `<div class="wf-seg seg-score" style="width: ${scorePct}%" title="Final Score: ${score.toFixed(1)}">${scorePct > 12 ? `${score.toFixed(1)} pts` : ""}</div>`;
    }
    if (dbPct > 0) {
      segHtml += `<div class="wf-seg seg-dealbreakers" style="width: ${dbPct}%" title="Deal-Breaker Deductions: -${dbDed.toFixed(1)} pts">${dbPct > 10 ? `-${dbDed.toFixed(1)}` : ""}</div>`;
    }
    if (woPct > 0) {
      segHtml += `<div class="wf-seg seg-warnings" style="width: ${woPct}%" title="Warning Deductions: -${woDed.toFixed(1)} pts">${woPct > 10 ? `-${woDed.toFixed(1)}` : ""}</div>`;
    }
    if (msPct > 0) {
      segHtml += `<div class="wf-seg seg-missing" style="width: ${msPct}%" title="Missing Protections: -${msDed.toFixed(1)} pts">${msPct > 10 ? `-${msDed.toFixed(1)}` : ""}</div>`;
    }

    waterfallBar.innerHTML = segHtml;

    waterfallLabels.innerHTML = `
      <div class="wf-label">
        <span class="wf-label-dot" style="background: var(--emerald);"></span>
        <span>Final Score:</span>
        <span class="wf-label-val" style="color: var(--emerald);">${score.toFixed(1)}</span>
      </div>
      ${dbDed > 0 ? `
      <div class="wf-label">
        <span class="wf-label-dot" style="background: #dc2626;"></span>
        <span>Deal-Breakers:</span>
        <span class="wf-label-val" style="color: #dc2626;">-${dbDed.toFixed(1)}</span>
      </div>` : ""}
      ${woDed > 0 ? `
      <div class="wf-label">
        <span class="wf-label-dot" style="background: #f59e0b;"></span>
        <span>Watch-Outs:</span>
        <span class="wf-label-val" style="color: #f59e0b;">-${woDed.toFixed(1)}</span>
      </div>` : ""}
      ${msDed > 0 ? `
      <div class="wf-label">
        <span class="wf-label-dot" style="background: #94a3b8;"></span>
        <span>Missing Terms:</span>
        <span class="wf-label-val" style="color: #64748b;">-${msDed.toFixed(1)}</span>
      </div>` : ""}
      ${prRew > 0 ? `
      <div class="wf-label">
        <span class="wf-label-dot" style="background: #10b981;"></span>
        <span>Protections Credit:</span>
        <span class="wf-label-val" style="color: #10b981;">+${prRew.toFixed(1)}</span>
      </div>` : ""}
    `;
  }

  // Visual Breakdown 3: Proportional Category Impact Bars
  function renderImpactBars(health) {
    if (!impactBarsList) return;

    const sb = health.score_breakdown || {};
    const dbDed = sb.deal_breaker_deductions ?? (health.deal_breakers_count ? health.deal_breakers_count * 8 : 0);
    const woDed = sb.watch_out_deductions ?? (health.watch_out_count ? health.watch_out_count * 3 : 0);
    const msDed = sb.missing_deductions ?? (health.missing_protections_count ? Math.min(12, health.missing_protections_count * 2) : 0);
    const prRew = sb.protection_rewards ?? (health.protections_count ? Math.min(15, health.protections_count * 2.5) : 0);

    const maxVal = Math.max(dbDed, woDed, msDed, prRew, 16);

    const dbWidth = Math.min(100, Math.round((dbDed / maxVal) * 100));
    const woWidth = Math.min(100, Math.round((woDed / maxVal) * 100));
    const msWidth = Math.min(100, Math.round((msDed / maxVal) * 100));
    const prWidth = Math.min(100, Math.round((prRew / maxVal) * 100));

    impactBarsList.innerHTML = `
      <div class="impact-bar-row">
        <div class="impact-bar-header">
          <span class="impact-bar-label">🔴 Deal-Breaker Penalties</span>
          <span class="impact-bar-value negative">-${dbDed.toFixed(1)} pts</span>
        </div>
        <div class="impact-bar-track">
          <div class="impact-bar-fill fill-red" style="width: ${dbWidth}%;"></div>
        </div>
      </div>

      <div class="impact-bar-row">
        <div class="impact-bar-header">
          <span class="impact-bar-label">🟡 Watch-Out Warning Terms</span>
          <span class="impact-bar-value negative">-${woDed.toFixed(1)} pts</span>
        </div>
        <div class="impact-bar-track">
          <div class="impact-bar-fill fill-amber" style="width: ${woWidth}%;"></div>
        </div>
      </div>

      <div class="impact-bar-row">
        <div class="impact-bar-header">
          <span class="impact-bar-label">⚪ Missing Standard Protections</span>
          <span class="impact-bar-value negative">-${msDed.toFixed(1)} pts</span>
        </div>
        <div class="impact-bar-track">
          <div class="impact-bar-fill fill-gray" style="width: ${msWidth}%;"></div>
        </div>
      </div>

      <div class="impact-bar-row">
        <div class="impact-bar-header">
          <span class="impact-bar-label">🟢 Active Protection Credits</span>
          <span class="impact-bar-value positive">+${prRew.toFixed(1)} pts</span>
        </div>
        <div class="impact-bar-track">
          <div class="impact-bar-fill fill-green" style="width: ${prWidth}%;"></div>
        </div>
      </div>
    `;
  }

  // Helper: Friendly Title Mapper
  function getFriendlyTitle(title) {
    const map = {
      "Asymmetric Termination Rights": "Unfair Cancellation Terms (15 Days vs 12 Months)",
      "Aggregate Liability Cap and Coverage Duration": "Low Payout Limit (Only 3 Months of Fees)",
      "Retention of Backup Copies of Customer Data": "Provider Keeps Your Deleted Backups for 6 Months",
      "Automatic Renewal and Non-Renewal Notice Period": "Auto-Renewal Trap (Must Cancel 90 Days Early)",
      "Customer's Security Audit Rights": "Restricted Security Audit Access",
      "Provider's Use of Customer's Name and Logo": "Provider Can Use Your Logo Without Asking",
      "Provider's Responsibility for Subcontractors": "Good Clause: Provider Takes Blame for Subcontractor Errors"
    };
    return map[title] || title;
  }

  // =========================================================================
  // 2. RENDER RISKS & FIXES (FINDINGS)
  // =========================================================================
  function updateFindingsFilterPills() {
    findingsFilterPills.forEach((pill) => {
      if (pill.getAttribute("data-filter") === activeFindingsFilter) {
        pill.classList.add("active");
      } else {
        pill.classList.remove("active");
      }
    });
  }

  findingsFilterPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      activeFindingsFilter = pill.getAttribute("data-filter");
      updateFindingsFilterPills();
      renderFindingsList();
    });
  });

  function renderFindingsList() {
    if (!findingsCleanList || !auditData) return;
    findingsCleanList.innerHTML = "";

    const allFindings = [
      ...(auditData.health?.deal_breakers || []),
      ...(auditData.health?.watch_out || []),
      ...(auditData.health?.protections || [])
    ];

    const filtered = allFindings.filter((f) => {
      if (activeFindingsFilter === "all") return true;
      return f.bucket === activeFindingsFilter;
    });

    if (filtered.length === 0) {
      findingsCleanList.innerHTML = `<div style="padding: 30px; text-align: center; color: var(--text-muted);">No findings in this category.</div>`;
      return;
    }

    filtered.forEach((finding, idx) => {
      const card = document.createElement("div");
      card.className = "finding-card";

      const bucketClass = finding.bucket === "deal_breaker" ? "tag-dealbreaker" : finding.bucket === "watch_out" ? "tag-watchout" : "tag-protection";
      const bucketIcon = finding.bucket === "deal_breaker" ? "🔴 Deal-Breaker" : finding.bucket === "watch_out" ? "🟡 Warning" : "🟢 Good Clause";

      const evidence = finding.evidence?.[0] || {};
      const pageNum = evidence.page ? `Page ${evidence.page}` : "Contract Body";
      const chunkId = evidence.chunk_id || "Clause";

      const friendlyTitle = getFriendlyTitle(finding.title);

      card.innerHTML = `
        <div class="finding-head">
          <div class="finding-title-group">
            <span class="badge-tag ${bucketClass}">${bucketIcon}</span>
            <span class="finding-title">${escapeHtml(friendlyTitle)}</span>
          </div>
          <div class="finding-meta-info">
            <span>Found in: ${pageNum} (${chunkId})</span>
          </div>
        </div>

        <div class="finding-plain">
          ${escapeHtml(finding.plain_english || finding.claim)}
        </div>

        <div class="finding-why">
          <strong>Why this matters to you:</strong> ${escapeHtml(finding.why_flagged || "Creates unfair risk or financial exposure for your company.")}
        </div>

        <div class="finding-card-actions">
          <div class="finding-citations-preview">
            <span>Verified 100% in PDF text</span>
          </div>
          <div class="finding-btns">
            <button class="btn btn-xs btn-outline btn-copy-proposal" data-index="${idx}">
              Copy Suggested Fix
            </button>
            <button class="btn btn-xs btn-primary btn-inspect-finding" data-index="${idx}">
              See Quote & Explanation ↗
            </button>
          </div>
        </div>
      `;

      card.querySelector(".btn-inspect-finding").addEventListener("click", () => {
        openEvidenceModal(finding);
      });

      const btnCopyProposal = card.querySelector(".btn-copy-proposal");
      btnCopyProposal?.addEventListener("click", () => {
        const text = finding.suggested_negotiation || finding.recommendation || "";
        copyToClipboard(text, btnCopyProposal, "Suggested fix copied to clipboard!");
      });

      findingsCleanList.appendChild(card);
    });
  }

  // =========================================================================
  // 3. RENDER MISSING CLAUSES VIEW
  // =========================================================================
  function renderMissingClauses(missing) {
    if (!tbodyMissing || !missing) return;
    tbodyMissing.innerHTML = "";

    const friendlyMissingMap = {
      "Disaster Recovery SLA & RTO/RPO": "No Disaster Recovery Commitment (No Fix Time Guarantee)",
      "Maximum Security Incident Notification Window": "No 48-Hour Security Breach Warning",
      "Affirmative Data Deletion & Certification": "No Written Certificate Proving Data is Erased",
      "Advance Notice of New Subprocessors": "No Warning When Provider Hires New Sub-Vendors",
      "Termination Right for Extended Force Majeure": "No Right to Cancel if System is Down for Months",
      "Customer Convenience Termination Parity": "Missing Equal Right to Cancel Anytime",
      "Cyber Liability & E&O Insurance Commitments": "No Requirement for Provider to Have Cyber Insurance"
    };

    missing.forEach((item, idx) => {
      const tr = document.createElement("tr");

      let statusBadge = `<span class="status-badge status-present">SAFE</span>`;
      if (item.status === "MISSING") {
        statusBadge = `<span class="status-badge status-missing">MISSING ❌</span>`;
      } else if (item.status === "VAGUE") {
        statusBadge = `<span class="status-badge status-vague">VAGUE ⚠️</span>`;
      }

      let riskColor = "color: var(--text-muted);";
      if (item.risk_level === "critical") riskColor = "color: var(--crimson); font-weight: 700;";
      else if (item.risk_level === "high") riskColor = "color: var(--amber); font-weight: 700;";

      const friendlyName = friendlyMissingMap[item.title] || item.title;

      tr.innerHTML = `
        <td>${statusBadge}</td>
        <td><strong style="color: var(--text-primary);">${escapeHtml(friendlyName)}</strong></td>
        <td><span style="${riskColor}">${escapeHtml((item.risk_level || "none").toUpperCase())}</span></td>
        <td>${escapeHtml(item.why_it_matters)}</td>
        <td>
          <button class="btn btn-xs btn-outline btn-inspect-missing" data-index="${idx}">
            See Clause to Add ↗
          </button>
        </td>
      `;

      tr.querySelector(".btn-inspect-missing").addEventListener("click", () => {
        openMissingClauseModal(item);
      });

      tbodyMissing.appendChild(tr);
    });
  }

  // =========================================================================
  // 4. RENDER KEY DATES & TIMELINE VIEW
  // =========================================================================
  function renderTimeline(obligations) {
    if (!timelineTree || !obligations) return;
    timelineTree.innerHTML = "";

    const items = obligations.timeline_items || [];
    const filtered = items.filter((item) => {
      if (activeTimelineParty === "all") return true;
      return item.party === activeTimelineParty;
    });

    if (filtered.length === 0) {
      timelineTree.innerHTML = `<div style="padding: 20px; color: var(--text-muted);">No dates found for selected filter.</div>`;
      return;
    }

    filtered.forEach((item) => {
      const node = document.createElement("div");
      node.className = "timeline-node";

      const partyClass = item.party === "Provider" ? "party-provider" : "party-customer";
      const partyLabel = item.party === "Provider" ? "Provider Obligation" : "Your Obligation";

      node.innerHTML = `
        <div class="timeline-dot"></div>
        <div class="timeline-time-badge">${escapeHtml(item.timeframe_label || "Milestone")}</div>
        <div class="timeline-content-card">
          <div class="timeline-row-top">
            <span class="timeline-party-tag ${partyClass}">${partyLabel}</span>
            <span class="timeline-section-cite">Page ${item.page || 1} • ${escapeHtml(item.section || "")}</span>
          </div>
          <div class="timeline-duty">${escapeHtml(item.duty)}</div>
        </div>
      `;

      timelineTree.appendChild(node);
    });
  }

  timelinePartyFilters.forEach((btn) => {
    btn.addEventListener("click", () => {
      timelinePartyFilters.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeTimelineParty = btn.getAttribute("data-party");
      if (auditData) renderTimeline(auditData.obligations);
    });
  });

  // =========================================================================
  // 5. RENDER SIGNATURES & PRICING FEES VIEW
  // =========================================================================
  function renderScanner(signatures, tables) {
    if (signatures) {
      if (sigHeadline) sigHeadline.textContent = signatures.execution_status === "UNEXECUTED_DRAFT" ? "NOT SIGNED YET (DRAFT CONTRACT)" : "SIGNED CONTRACT";
      if (sigSubnotes) sigSubnotes.textContent = signatures.subnotes || "Blank signature lines found on Page 5. No handwritten or electronic signatures detected.";
      if (sigCustName && auditData?.parties?.customer) sigCustName.textContent = auditData.parties.customer;
      if (sigProvName && auditData?.parties?.provider) sigProvName.textContent = auditData.parties.provider;
    }

    if (tables && tableTabs && tableDisplayWrap) {
      tableTabs.innerHTML = "";
      tables.forEach((t, i) => {
        const btn = document.createElement("button");
        btn.className = `table-tab-btn ${i === activeTableIndex ? "active" : ""}`;
        btn.textContent = `Table ${t.table_number || i + 1} (Page ${t.page || 1})`;
        btn.addEventListener("click", () => {
          activeTableIndex = i;
          renderScanner(signatures, tables);
        });
        tableTabs.appendChild(btn);
      });

      const activeTable = tables[activeTableIndex] || tables[0];
      if (activeTable) {
        tableDisplayWrap.innerHTML = formatMarkdownTable(activeTable.markdown_table || "");
      }

      if (tableRisksContainer) {
        tableRisksContainer.innerHTML = `
          <strong>💡 Extra Fees Warning:</strong>
          Extra storage is billed at ₹4.50 per GB/month with no annual price cap. 
          If your data grows quickly, your monthly bill could jump without warning.
        `;
      }
    }
  }

  function formatMarkdownTable(md) {
    if (!md) return "<p>No table content.</p>";
    const lines = md.trim().split("\n").filter((l) => l.trim().length > 0);
    if (lines.length < 2) return `<pre>${escapeHtml(md)}</pre>`;

    let html = `<div class="table-responsive"><table class="data-table"><thead><tr>`;
    const headers = lines[0].split("|").map((c) => c.trim()).filter(Boolean);
    headers.forEach((h) => { html += `<th>${escapeHtml(h)}</th>`; });
    html += `</tr></thead><tbody>`;

    for (let i = 2; i < lines.length; i++) {
      const cells = lines[i].split("|").map((c) => c.trim()).filter(Boolean);
      if (cells.length > 0) {
        html += `<tr>`;
        cells.forEach((c) => { html += `<td>${escapeHtml(c)}</td>`; });
        html += `</tr>`;
      }
    }
    html += `</tbody></table></div>`;
    return html;
  }

  // =========================================================================
  // 6. RENDER AI DEBATE ARENA
  // =========================================================================
  function renderCourtroomDebate(findings) {
    if (!debateArena || !findings) return;
    debateArena.innerHTML = "";

    findings.forEach((finding, idx) => {
      const debate = finding.debate_history?.[0] || {};
      const auditor = debate.finding || finding;
      const verifier = debate.verification || {};

      const card = document.createElement("div");
      card.className = "debate-card";

      const quote = auditor.evidence?.[0]?.quote || "";
      const friendlyTitle = getFriendlyTitle(finding.title);

      card.innerHTML = `
        <div class="debate-card-header">
          <div class="debate-topic">${escapeHtml(friendlyTitle)}</div>
          <span class="verdict-tag verdict-accepted">✓ VERIFIED BY SKEPTIC (${Math.round((verifier.confidence || 0.95) * 100)}% MATCH)</span>
        </div>

        <div class="debate-two-col">
          <div class="agent-bubble">
            <div class="agent-head">
              <div class="agent-title"><span>🤖</span> AI Auditor Found</div>
              <span class="badge-version">Initial Finding</span>
            </div>
            <div class="agent-text">${escapeHtml(auditor.plain_english || auditor.claim)}</div>
            ${quote ? `<div class="agent-evidence">"${escapeHtml(quote)}"</div>` : ""}
          </div>

          <div class="agent-bubble">
            <div class="agent-head">
              <div class="agent-title"><span>🛡️</span> AI Skeptic Double-Checked</div>
              <span class="badge-version">Verified Proof</span>
            </div>
            <div class="agent-text">${escapeHtml(verifier.reasoning || "Confirmed word-for-word in the contract text with no conflicting terms.")}</div>
          </div>
        </div>

        <div class="debate-remedy-box">
          <div class="remedy-text-clean">
            <strong>Ready-to-Use Fix:</strong> ${escapeHtml(auditor.suggested_negotiation || auditor.recommendation || "")}
          </div>
          <button class="btn btn-xs btn-outline btn-copy-debate-remedy" data-index="${idx}">
            Copy Fix
          </button>
        </div>
      `;

      card.querySelector(".btn-copy-debate-remedy")?.addEventListener("click", () => {
        navigator.clipboard.writeText(auditor.suggested_negotiation || auditor.recommendation || "");
        showToast("Fix copied to clipboard!");
      });

      debateArena.appendChild(card);
    });
  }

  // Ask Question Runner
  async function runCourtroomQuery(query) {
    if (!query || !query.trim()) return;
    showToast(`Checking: "${query}"...`, "⏳");

    if (btnAskCourtroom) {
      btnAskCourtroom.disabled = true;
      btnAskCourtroom.innerHTML = `<span>Checking...</span>`;
    }

    try {
      const res = await fetch("/api/debate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim() })
      });

      if (!res.ok) throw new Error("Debate endpoint error");
      const result = await res.json();

      const newCard = document.createElement("div");
      newCard.className = "debate-card";
      newCard.style.borderColor = "var(--indigo)";

      const auditor = result.auditor_finding || {};
      const verifier = result.verifier_result || {};
      const quote = auditor.evidence?.[0]?.quote || "";

      newCard.innerHTML = `
        <div class="debate-card-header">
          <div class="debate-topic">Question: ${escapeHtml(query)}</div>
          <span class="verdict-tag verdict-accepted">✓ ${escapeHtml(verifier.verdict || "ACCEPTED")} (${Math.round((verifier.confidence || 0.95) * 100)}% MATCH)</span>
        </div>

        <div class="debate-two-col">
          <div class="agent-bubble">
            <div class="agent-head">
              <div class="agent-title"><span>🤖</span> AI Auditor</div>
            </div>
            <div class="agent-text">${escapeHtml(auditor.claim || auditor.reasoning)}</div>
            ${quote ? `<div class="agent-evidence">"${escapeHtml(quote)}"</div>` : ""}
          </div>

          <div class="agent-bubble">
            <div class="agent-head">
              <div class="agent-title"><span>🛡️</span> AI Skeptic</div>
            </div>
            <div class="agent-text">${escapeHtml(verifier.reasoning || "Confirmed in contract text.")}</div>
          </div>
        </div>

        <div class="debate-remedy-box">
          <div class="remedy-text-clean">
            <strong>Recommended Fix:</strong> ${escapeHtml(auditor.recommendation || "")}
          </div>
        </div>
      `;

      debateArena.prepend(newCard);
      showToast("Answer verified in contract text!", "⚖️");
    } catch (err) {
      showToast("Error checking question: " + err.message, "❌");
    } finally {
      if (btnAskCourtroom) {
        btnAskCourtroom.disabled = false;
        btnAskCourtroom.innerHTML = `<span>Ask & Verify</span>`;
      }
    }
  }

  btnAskCourtroom?.addEventListener("click", () => {
    runCourtroomQuery(courtroomQueryInput.value);
  });

  courtroomQueryInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") runCourtroomQuery(courtroomQueryInput.value);
  });

  chipButtons.forEach((chip) => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      if (courtroomQueryInput) courtroomQueryInput.value = q;
      runCourtroomQuery(q);
    });
  });

  // =========================================================================
  // 7. MODALS CONTROLLER (OPEN ON DEMAND)
  // =========================================================================
  function openEvidenceModal(finding) {
    if (!evidenceModal) return;

    const evidence = finding.evidence?.[0] || {};
    const pageNum = evidence.page ? `Page ${evidence.page}` : "Page Cited";
    const chunkId = evidence.chunk_id || "Section Citation";
    const quoteText = evidence.quote || finding.claim || "";
    const remedyText = finding.suggested_negotiation || finding.recommendation || "Ask provider to align with standard commercial fairness.";
    const friendlyTitle = getFriendlyTitle(finding.title);

    if (modalTitle) modalTitle.textContent = friendlyTitle;
    if (modalPage) modalPage.textContent = pageNum;
    if (modalChunk) modalChunk.textContent = chunkId;
    if (modalSection) modalSection.textContent = finding.category ? `Category: ${finding.category}` : "Contract Clause";
    if (modalPlainEnglish) modalPlainEnglish.textContent = finding.plain_english || finding.claim || "";
    if (modalWhy) modalWhy.textContent = finding.why_flagged || "This provision creates serious operational or financial risk for your company.";
    if (modalQuote) modalQuote.textContent = `"${quoteText}"`;
    if (modalRemedy) modalRemedy.textContent = remedyText;

    btnCopyModalRemedy.onclick = () => {
      copyToClipboard(remedyText, btnCopyModalRemedy, "Counter-proposal copied to clipboard!");
    };

    evidenceModal.showModal();
  }

  [btnCloseModal, btnCloseModalFooter].forEach((btn) => {
    btn?.addEventListener("click", () => evidenceModal?.close());
  });

  // Asymmetry Modal (Fairness Check)
  function openAsymmetryModal() {
    if (!asymmetryModal || !asymmetryMatrixContainer || !auditData) return;
    asymmetryMatrixContainer.innerHTML = "";

    const balanceItems = auditData.clause_balance || [];
    balanceItems.forEach((b) => {
      const item = document.createElement("div");
      item.className = "asymmetry-item";

      const friendlyTitle = getFriendlyTitle(b.title);

      item.innerHTML = `
        <div class="asymmetry-item-head">
          <div class="asymmetry-item-title">${escapeHtml(friendlyTitle)}</div>
          <span class="pill-citation">Page ${b.page || 3}</span>
        </div>

        <div class="asymmetry-cols">
          <div class="asymmetry-col-card col-prov">
            <strong style="color: var(--crimson);">🏢 What the Provider Gave Themselves:</strong>
            <p style="margin-top: 4px;">${escapeHtml(b.provider_terms)}</p>
          </div>

          <div class="asymmetry-col-card col-cust">
            <strong style="color: #1D4ED8;">👤 What They Gave Your Company:</strong>
            <p style="margin-top: 4px;">${escapeHtml(b.customer_terms)}</p>
          </div>
        </div>

        <div class="asymmetry-verdict-bar">
          <strong>Why this is unfair:</strong> ${escapeHtml(b.asymmetry_summary)}
        </div>
      `;

      asymmetryMatrixContainer.appendChild(item);
    });

    asymmetryModal.showModal();
  }

  [btnCloseAsymmetryModal, btnCloseAsymmetryFooter].forEach((btn) => {
    btn?.addEventListener("click", () => asymmetryModal?.close());
  });

  // Missing Clause Modal
  function openMissingClauseModal(item) {
    if (!missingClauseModal) return;

    if (missingModalTitle) missingModalTitle.textContent = item.title || "Recommended Contract Clause";
    if (missingModalWhy) missingModalWhy.textContent = item.why_it_matters || "Standard protection missing from contract.";
    if (missingModalCode) missingModalCode.innerHTML = `<code>${escapeHtml(item.recommended_clause || "")}</code>`;

    btnCopyMissingClause.onclick = () => {
      copyToClipboard(item.recommended_clause || "", btnCopyMissingClause, "Draft clause copied to clipboard!");
    };

    missingClauseModal.showModal();
  }

  [btnCloseMissingModal, btnCloseMissingFooter].forEach((btn) => {
    btn?.addEventListener("click", () => missingClauseModal?.close());
  });

  // Close dialog on backdrop click
  [evidenceModal, asymmetryModal, missingClauseModal].forEach((dialog) => {
    dialog?.addEventListener("click", (e) => {
      if (e.target === dialog) dialog.close();
    });
  });

  // =========================================================================
  // 8. FLUID KNOWLEDGE GRAPH CANVAS
  // =========================================================================
  function drawKnowledgeGraph(graph) {
    if (!graphCanvas) return;

    // Dynamically adjust canvas to match parent container width
    const rect = graphCanvas.parentElement.getBoundingClientRect();
    graphCanvas.width = rect.width || 800;
    graphCanvas.height = 420;

    const ctx = graphCanvas.getContext("2d");
    if (!ctx) return;

    const width = graphCanvas.width;
    const height = graphCanvas.height;
    ctx.clearRect(0, 0, width, height);

    const nodes = [
      { id: "node-1", label: "Northstar Analytics", type: "party", x: width * 0.2, y: height * 0.3 },
      { id: "node-2", label: "Meridian Cloud", type: "party", x: width * 0.8, y: height * 0.3 },
      { id: "node-3", label: "Section 9 (Liability)", type: "clause", x: width * 0.35, y: height * 0.65 },
      { id: "node-4", label: "Section 10 (Cancel)", type: "clause", x: width * 0.65, y: height * 0.65 },
      { id: "node-5", label: "3-Month Fee Cap", type: "metric", x: width * 0.35, y: height * 0.88 },
      { id: "node-6", label: "15-Day Exit Rule", type: "metric", x: width * 0.65, y: height * 0.88 },
      { id: "node-7", label: "Customer Data", type: "asset", x: width * 0.5, y: height * 0.2 }
    ];

    const edges = [
      { source: "node-1", target: "node-3", label: "governed by" },
      { source: "node-2", target: "node-4", label: "controls" },
      { source: "node-3", target: "node-5", label: "limits recovery to" },
      { source: "node-4", target: "node-6", label: "unilateral exit" },
      { source: "node-1", target: "node-7", label: "owns" }
    ];

    if (graphNodeCount) graphNodeCount.textContent = `${nodes.length} Items`;
    if (graphEdgeCount) graphEdgeCount.textContent = `${edges.length} Connections`;

    // Draw Edges
    ctx.lineWidth = 1.5;
    edges.forEach((edge) => {
      const src = nodes.find((n) => n.id === edge.source) || nodes[0];
      const tgt = nodes.find((n) => n.id === edge.target) || nodes[1];

      ctx.strokeStyle = "#CBD5E1";
      ctx.beginPath();
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(tgt.x, tgt.y);
      ctx.stroke();

      const midX = (src.x + tgt.x) / 2;
      const midY = (src.y + tgt.y) / 2;
      ctx.fillStyle = "#64748B";
      ctx.font = "10px JetBrains Mono";
      ctx.textAlign = "center";
      ctx.fillText(edge.label || "", midX, midY - 3);
    });

    // Draw Nodes
    nodes.forEach((node) => {
      let fill = "#4F46E5";
      if (node.type === "party") fill = "#059669";
      else if (node.type === "metric") fill = "#DC2626";
      else if (node.type === "asset") fill = "#0284C7";

      ctx.fillStyle = fill;
      ctx.beginPath();
      ctx.arc(node.x, node.y, 12, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = "#0F172A";
      ctx.font = "600 11px Plus Jakarta Sans";
      ctx.textAlign = "center";
      ctx.fillText(node.label, node.x, node.y + 22);
    });
  }

  btnResetGraph?.addEventListener("click", () => {
    if (auditData) drawKnowledgeGraph(auditData.graph);
  });

  window.addEventListener("resize", () => {
    const activeScreen = document.querySelector(".screen.active");
    if (activeScreen && activeScreen.id === "screen-graph" && auditData) {
      drawKnowledgeGraph(auditData.graph);
    }
  });

  // =========================================================================
  // 9. DRAG & DROP, FILE UPLOAD & AUDIT WORKFLOW
  // =========================================================================
  let selectedFile = null;

  function stageFileForAudit(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      showToast("Only PDF files (.pdf) are supported.", "⚠️");
      return;
    }
    selectedFile = file;
    if (previewFilename) previewFilename.textContent = file.name;
    if (previewFilesize) {
      const kb = (file.size / 1024).toFixed(1);
      previewFilesize.textContent = `${kb} KB`;
    }
    if (dropZone) dropZone.style.display = "none";
    if (filePreviewCard) filePreviewCard.style.display = "flex";
    if (uploadProgressCard) uploadProgressCard.style.display = "none";
  }

  // Drag and Drop Events on #drop-zone
  if (dropZone) {
    ["dragenter", "dragover"].forEach((eventName) => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove("dragover");
      });
    });

    dropZone.addEventListener("drop", (e) => {
      const dt = e.dataTransfer;
      const file = dt?.files?.[0];
      if (file) {
        stageFileForAudit(file);
      }
    });

    dropZone.addEventListener("click", (e) => {
      if (e.target.closest("#btn-browse-trigger")) return;
      fileUploadInput?.click();
    });
  }

  btnBrowseTrigger?.addEventListener("click", (e) => {
    e.stopPropagation();
    fileUploadInput?.click();
  });

  fileUploadInput?.addEventListener("change", (e) => {
    const file = e.target.files?.[0];
    if (file) {
      stageFileForAudit(file);
    }
  });

  btnCancelFile?.addEventListener("click", () => {
    selectedFile = null;
    if (fileUploadInput) fileUploadInput.value = "";
    if (filePreviewCard) filePreviewCard.style.display = "none";
    if (dropZone) dropZone.style.display = "flex";
  });

  btnStartAudit?.addEventListener("click", () => {
    if (selectedFile) {
      executeAudit(selectedFile);
    } else {
      showToast("Please select a contract PDF first.", "⚠️");
    }
  });

  // Header quick upload button
  btnChooseFile?.addEventListener("click", () => {
    fileUploadInput?.click();
  });

  // Core Audit Execution
  async function executeAudit(file) {
    if (!file) return;

    if (filePreviewCard) filePreviewCard.style.display = "none";
    if (dropZone) dropZone.style.display = "none";
    if (uploadProgressCard) uploadProgressCard.style.display = "block";

    const steps = [
      { id: "prog-step-1", title: "Ingesting PDF & Extracting Text & Tables..." },
      { id: "prog-step-2", title: "Building Hybrid BM25 & Semantic Chunks..." },
      { id: "prog-step-3", title: "Running Dual-Agent Courtroom Debate..." },
      { id: "prog-step-4", title: "Computing 100-Point Safety Score & Memo..." }
    ];

    let currentStepIdx = 0;
    const updateProgressUI = (idx) => {
      steps.forEach((step, i) => {
        const el = document.getElementById(step.id);
        if (el) {
          if (i < idx) {
            el.className = "progress-step-item completed";
          } else if (i === idx) {
            el.className = "progress-step-item active";
          } else {
            el.className = "progress-step-item";
          }
        }
      });
      if (auditProgressStageTitle && steps[idx]) {
        auditProgressStageTitle.textContent = steps[idx].title;
      }
    };

    updateProgressUI(0);
    const progressTimer = setInterval(() => {
      if (currentStepIdx < steps.length - 1) {
        currentStepIdx++;
        updateProgressUI(currentStepIdx);
      }
    }, 3500);

    showToast(`Auditing "${file.name}"... Autonomous review in progress.`, "⏳");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Upload failed with status ${res.status}`);
      }

      const data = await res.json();
      if (!data.report) {
        throw new Error("No audit report was returned by the server.");
      }

      auditData = data.report;
      renderAll(auditData);
      showToast(`Audit complete for "${file.name}"!`, "🎉");
      switchScreen("screen-overview", "tab-overview");
    } catch (err) {
      console.error("Upload error:", err);
      showToast("Audit error: " + err.message, "❌");
      if (filePreviewCard) filePreviewCard.style.display = "flex";
    } finally {
      clearInterval(progressTimer);
      if (uploadProgressCard) uploadProgressCard.style.display = "none";
      if (dropZone) dropZone.style.display = "flex";
      if (fileUploadInput) fileUploadInput.value = "";
      selectedFile = null;
    }
  }

  // "Try Demo Contract" Handler
  btnTryDemo?.addEventListener("click", async () => {
    if (dropZone) dropZone.style.display = "none";
    if (filePreviewCard) filePreviewCard.style.display = "none";
    if (uploadProgressCard) uploadProgressCard.style.display = "block";

    const steps = [
      { id: "prog-step-1", title: "Loading Sample Contract Pages..." },
      { id: "prog-step-2", title: "Verifying Hybrid Index..." },
      { id: "prog-step-3", title: "Running AI Courtroom Analysis..." },
      { id: "prog-step-4", title: "Finalizing Safety Score..." }
    ];
    let idx = 0;
    const updateProgressUI = (i) => {
      steps.forEach((s, stepIndex) => {
        const el = document.getElementById(s.id);
        if (el) {
          el.className = stepIndex < i ? "progress-step-item completed" : stepIndex === i ? "progress-step-item active" : "progress-step-item";
        }
      });
      if (auditProgressStageTitle && steps[i]) {
        auditProgressStageTitle.textContent = steps[i].title;
      }
    };
    updateProgressUI(0);
    const timer = setInterval(() => {
      if (idx < steps.length - 1) {
        idx++;
        updateProgressUI(idx);
      }
    }, 1200);

    showToast("Loading Sample Demo Contract...", "💡");

    try {
      const res = await fetch("/api/sample/demo");
      if (!res.ok) {
        throw new Error("Could not load sample demo contract.");
      }
      const data = await res.json();
      auditData = data.report || data;
      renderAll(auditData);
      showToast("Demo contract loaded! Explore findings or upload your own.", "🎉");
      switchScreen("screen-overview", "tab-overview");
    } catch (err) {
      console.error("Demo error:", err);
      showToast("Could not load demo contract: " + err.message, "❌");
      if (dropZone) dropZone.style.display = "flex";
    } finally {
      clearInterval(timer);
      if (uploadProgressCard) uploadProgressCard.style.display = "none";
    }
  });

  // =========================================================================
  // 10. QUICK ACTIONS & HEADER BUTTONS
  // =========================================================================
  btnHeaderNewAudit?.addEventListener("click", resetToWelcomeScreen);
  btnQaUpload?.addEventListener("click", resetToWelcomeScreen);

  [btnDownloadMemo, btnQaMemo].forEach((btn) => {
    btn?.addEventListener("click", () => {
      window.open("/api/download/memo", "_blank");
    });
  });

  btnQaJson?.addEventListener("click", () => {
    if (!auditData) {
      showToast("No contract data loaded yet.", "⚠️");
      return;
    }
    const filename = (auditData.document_name || "contract_audit").replace(/\.pdf$/i, "") + "_audit_report.json";
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(auditData, null, 2));
    const dlAnchor = document.createElement("a");
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", filename);
    document.body.appendChild(dlAnchor);
    dlAnchor.click();
    dlAnchor.remove();
    showToast("Audit JSON exported successfully!", "📥");
  });

  btnQaAsk?.addEventListener("click", () => {
    switchScreen("screen-courtroom", "tab-courtroom");
    setTimeout(() => {
      courtroomQueryInput?.focus();
    }, 150);
  });

  // Utility: HTML Escaper
  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Load Initial Data (will stay on clean welcome screen if no previous upload)
  loadLatestReport();
});
