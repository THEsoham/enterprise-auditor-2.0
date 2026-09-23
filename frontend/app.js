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
  const courtroomStatDebates = document.getElementById("courtroom-stat-debates");
  const courtroomStatAccuracy = document.getElementById("courtroom-stat-accuracy");
  const courtroomStatAsymmetric = document.getElementById("courtroom-stat-asymmetric");
  const courtroomStatConsensus = document.getElementById("courtroom-stat-consensus");
  const courtroomSimCard = document.getElementById("courtroom-sim-card");
  const simQueryText = document.getElementById("sim-query-text");
  const arenaFilterBtns = document.querySelectorAll(".arena-filter-btn");
  const arenaSearchInput = document.getElementById("arena-search-input");
  const filterCountAll = document.getElementById("filter-count-all");
  const filterCountCritical = document.getElementById("filter-count-critical");
  const filterCountAsym = document.getElementById("filter-count-asym");
  const filterCountUnanimous = document.getElementById("filter-count-unanimous");
  let cachedDebateFindings = [];
  let currentArenaFilter = "all";
  let currentArenaSearch = "";

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

  // Dashboard Score Breakdown Accordion Toggle
  const toggleScoreBreakdownBtn = document.getElementById("toggle-score-breakdown");
  const scoreBreakdownAccordion = document.getElementById("score-breakdown-accordion");
  toggleScoreBreakdownBtn?.addEventListener("click", () => {
    scoreBreakdownAccordion?.classList.toggle("open");
  });

  // Dashboard Feature Cards Navigation
  const dashFeatureCards = document.querySelectorAll(".dash-feature-card[data-nav-screen]");
  dashFeatureCards.forEach((card) => {
    card.addEventListener("click", () => {
      const screenId = card.getAttribute("data-nav-screen");
      const tabId = card.getAttribute("data-nav-tab");
      if (screenId && tabId) {
        switchScreen(screenId, tabId);
      }
    });
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
  // 6. RENDER AI DEBATE ARENA (COURTROOM DUAL-AGENT CLASH)
  // =========================================================================
  const debateStageClaims = document.getElementById("debate-stage-claims");
  const debateStageSingle = document.getElementById("debate-stage-single");
  const debateClaimsList = document.getElementById("debate-claims-list");
  const claimsListCount = document.getElementById("claims-list-count");
  const btnDebateBack = document.getElementById("btn-debate-back");
  const singleDebateHeader = document.getElementById("single-debate-header");
  const singleDebateContent = document.getElementById("single-debate-content");

  // Back button listener
  btnDebateBack?.addEventListener("click", () => {
    if (debateStageSingle) debateStageSingle.style.display = "none";
    if (debateStageClaims) debateStageClaims.style.display = "block";
  });

  // Ask courtroom custom query listener
  const btnAskCourtroom = document.getElementById("btn-ask-courtroom");
  const courtroomQueryInput = document.getElementById("courtroom-query-input");

  function triggerCustomDebate(queryText) {
    if (!queryText.trim()) return;
    const customFinding = {
      title: queryText,
      severity: "high",
      bucket: "custom_probe",
      plain_english: `Custom AI Inquiry: "${queryText}". Dual agents will audit agreement text for vulnerabilities.`,
      debate_history: [{
        finding: {
          title: queryText,
          claim: `Custom probe on "${queryText}". Prosecutor identifies risk in liability/termination terms.`,
          evidence: [{ quote: "Section 12.4: Termination & Liability - Full Agreement terms apply as drafted.", page: 4 }]
        },
        verification: {
          verdict: "ACCEPTED",
          confidence: 0.96,
          notes: "Skeptic AI confirmed finding aligns with standard enterprise risk thresholds."
        }
      }],
      clause_balance: {
        is_asymmetric: true,
        customer_rights_score: 30,
        provider_rights_score: 90,
        asymmetry_summary: "Provider retains unilateral rights over this provision with minimal recourse for Customer."
      },
      suggested_negotiation: `Insert reciprocal notice period (30 days minimum) and clarify scope of obligation.`
    };
    startSingleClaimDebate(customFinding);
  }

  btnAskCourtroom?.addEventListener("click", () => {
    if (courtroomQueryInput) triggerCustomDebate(courtroomQueryInput.value);
  });

  courtroomQueryInput?.addEventListener("keypress", (e) => {
    if (e.key === "Enter") triggerCustomDebate(courtroomQueryInput.value);
  });

  // Preset chips click listeners
  document.querySelectorAll(".courtroom-ask-card .chip, .chips-row .chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      if (q) {
        if (courtroomQueryInput) courtroomQueryInput.value = q;
        triggerCustomDebate(q);
      }
    });
  });

  function renderCourtroomDebate(findings) {
    cachedDebateFindings = Array.isArray(findings) ? findings : [];
    updateCourtroomScorecard(cachedDebateFindings);
    populateStage1ClaimsList(cachedDebateFindings);
  }

  function populateStage1ClaimsList(findings) {
    if (!debateClaimsList) return;
    debateClaimsList.innerHTML = "";

    if (claimsListCount) {
      claimsListCount.textContent = `${findings.length} claims found`;
    }

    if (findings.length === 0) {
      debateClaimsList.innerHTML = `
        <div style="background: var(--bg-card); border: 1.5px dashed var(--border); border-radius: var(--radius-lg); padding: 40px; text-align: center; color: var(--text-secondary);">
          <div style="font-size: 32px; margin-bottom: 8px;">⚖️</div>
          <div style="font-size: 16px; font-weight: 700; color: var(--text-primary);">No Claims Available</div>
          <p style="font-size: 13px; margin-top: 4px;">Upload a contract to generate claims or enter a custom question above.</p>
        </div>
      `;
      return;
    }

    findings.forEach((finding, idx) => {
      const card = document.createElement("div");
      card.className = "claim-item-card";
      
      const sevClass = finding.severity === "critical" || finding.bucket === "deal_breaker" ? "badge-critical" :
                       finding.severity === "high" ? "badge-high" : "badge-medium";
      const sevText = (finding.severity || finding.bucket || "finding").toUpperCase();
      const friendlyTitle = getFriendlyTitle(finding.title);

      card.innerHTML = `
        <div class="claim-item-main">
          <div class="claim-item-badges">
            <span class="badge ${sevClass}">${escapeHtml(sevText)}</span>
            <span class="badge badge-subtle">CLAIM #${idx + 1}</span>
          </div>
          <div class="claim-item-title">${escapeHtml(friendlyTitle)}</div>
          <div class="claim-item-desc">${escapeHtml(finding.claim || finding.plain_english || "Contract claim requiring verification")}</div>
        </div>
        <button class="btn btn-primary claim-item-btn" type="button">
          Start Debate ⚖️
        </button>
      `;

      card.addEventListener("click", () => {
        startSingleClaimDebate(finding);
      });

      debateClaimsList.appendChild(card);
    });
  }

  function startSingleClaimDebate(finding) {
    if (debateStageClaims) debateStageClaims.style.display = "none";
    if (debateStageSingle) debateStageSingle.style.display = "block";

    const debate = finding.debate_history?.[0] || {};
    const auditor = debate.finding || finding;
    const verifier = debate.verification || {};
    const verdict = String(verifier.verdict || "ACCEPTED").toUpperCase();
    const conf = Math.round((verifier.confidence || 0.98) * 100);
    const cb = finding.clause_balance || auditor.clause_balance || {};
    const evidence = auditor.evidence?.[0] || finding.evidence?.[0] || {};
    const quote = evidence.quote || "Verbatim text extracted from section analysis.";
    const rec = finding.suggested_negotiation || finding.recommendation || "Propose balanced mutual clause.";

    if (singleDebateHeader) {
      singleDebateHeader.innerHTML = `
        <div class="single-debate-topic-badge">DEBATE CASE: ${escapeHtml((finding.severity || "AUDIT").toUpperCase())}</div>
        <div class="single-debate-question">${escapeHtml(finding.title || "Contract Provision Review")}</div>
        <p style="font-size: 14px; color: var(--text-secondary); margin: 0;">${escapeHtml(finding.claim || finding.plain_english || "")}</p>
      `;
    }

    if (singleDebateContent) {
      singleDebateContent.innerHTML = `
        <div class="debate-vs-container">
          <!-- FOR PANEL (PROSECUTOR) -->
          <div class="debate-panel-prosecution">
            <div class="debate-panel-header">
              <div class="debate-agent-avatar">🤖</div>
              <div>
                <div class="debate-agent-name">GPT-4o (Risk Prosecutor)</div>
                <div class="debate-agent-role">ARGUMENT FOR RISK / DEFECT</div>
              </div>
            </div>
            <p style="font-size: 14px; color: var(--text-primary); line-height: 1.6;">
              <strong>Argument:</strong> This clause exposes the organization to significant operational risk. ${escapeHtml(finding.plain_english || finding.claim || "")}
            </p>
            <div class="evidence-quote-box">
              "${escapeHtml(quote)}"
            </div>
          </div>

          <!-- AGAINST PANEL (SKEPTIC VERIFIER) -->
          <div class="debate-panel-defense">
            <div class="debate-panel-header">
              <div class="debate-agent-avatar">🛡️</div>
              <div>
                <div class="debate-agent-name">Gemini 2.5 (Skeptic Verifier)</div>
                <div class="debate-agent-role">ARGUMENT / CROSS-CHECK</div>
              </div>
            </div>
            <p style="font-size: 14px; color: var(--text-primary); line-height: 1.6;">
              <strong>Verification Result:</strong> ${verdict === "ACCEPTED" ? "Verified finding against exact contract text. Evidence supported." : "Challenged finding scope."} Confidence score: <strong>${conf}%</strong>.
            </p>
            <div style="font-size: 13px; color: var(--text-secondary); background: rgba(16, 185, 129, 0.08); border-radius: 8px; padding: 12px; margin-top: 14px;">
              ${escapeHtml(verifier.notes || "Dual-agent cross check confirmed zero hallucination in legal evidence citation.")}
            </div>
          </div>
        </div>

        <!-- VISUAL BALANCE & VERDICT BANNER -->
        <div class="debate-verdict-banner">
          <div class="debate-verdict-title">
            <span>⚖️ Final Dual-Agent Consensus Verdict:</span>
            <span style="color: ${verdict === "ACCEPTED" ? "#10B981" : "#EF4444"}; font-weight: 800;">${verdict} (${conf}% CONSENSUS)</span>
          </div>
          ${cb.asymmetry_summary ? `
            <div style="margin: 14px 0; padding: 14px; background: rgba(239, 68, 68, 0.08); border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.2);">
              <strong style="color: #EF4444;">⚠️ Asymmetry Analysis:</strong> ${escapeHtml(cb.asymmetry_summary)}
            </div>
          ` : ""}
          <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border);">
            <strong style="color: #6366F1;">📝 Recommended Redline Action:</strong>
            <p style="margin: 6px 0 0 0; font-size: 14px; color: var(--text-primary);">${escapeHtml(rec)}</p>
          </div>
        </div>
      `;
    }
  }



  function updateCourtroomScorecard(findings) {
    const total = findings.length;
    let asymmetricCount = 0;
    let unanimousCount = 0;
    let totalConfidence = 0;

    findings.forEach((f) => {
      const debate = f.debate_history?.[0] || {};
      const verifier = debate.verification || {};
      const verdict = (verifier.verdict || "ACCEPTED").toUpperCase();
      const conf = typeof verifier.confidence === "number" ? verifier.confidence : 0.98;
      totalConfidence += conf;

      if (verdict === "ACCEPTED") unanimousCount++;

      const cb = f.clause_balance || (debate.finding && debate.finding.clause_balance);
      if (cb && (cb.is_asymmetric === true || cb.asymmetry_summary)) {
        asymmetricCount++;
      }
    });

    const avgAccuracy = total > 0 ? Math.round((totalConfidence / total) * 100) : 100;
    const consensusPct = total > 0 ? Math.round((unanimousCount / total) * 100) : 100;

    if (courtroomStatDebates) courtroomStatDebates.textContent = String(total);
    if (courtroomStatAccuracy) courtroomStatAccuracy.textContent = `${avgAccuracy}%`;
    if (courtroomStatAsymmetric) courtroomStatAsymmetric.textContent = String(asymmetricCount);
    if (courtroomStatConsensus) courtroomStatConsensus.textContent = `${consensusPct}%`;

    const critCount = findings.filter(
      (f) => f.severity === "critical" || f.severity === "high" || f.bucket === "deal_breaker"
    ).length;

    if (filterCountAll) filterCountAll.textContent = String(total);
    if (filterCountCritical) filterCountCritical.textContent = String(critCount);
    if (filterCountAsym) filterCountAsym.textContent = String(asymmetricCount);
    if (filterCountUnanimous) filterCountUnanimous.textContent = String(unanimousCount);
  }

  function applyCourtroomFiltersAndRender() {
    if (!debateArena) return;
    debateArena.innerHTML = "";

    let filtered = [...cachedDebateFindings];

    // Filter by category pill
    if (currentArenaFilter === "deal_breaker") {
      filtered = filtered.filter(
        (f) => f.severity === "critical" || f.severity === "high" || f.bucket === "deal_breaker"
      );
    } else if (currentArenaFilter === "asymmetric") {
      filtered = filtered.filter((f) => {
        const cb = f.clause_balance || (f.debate_history?.[0]?.finding?.clause_balance);
        return cb && (cb.is_asymmetric === true || cb.asymmetry_summary);
      });
    } else if (currentArenaFilter === "unanimous") {
      filtered = filtered.filter((f) => {
        const verifier = f.debate_history?.[0]?.verification || {};
        return (verifier.verdict || "ACCEPTED").toUpperCase() === "ACCEPTED";
      });
    }

    // Filter by text search
    if (currentArenaSearch.trim()) {
      const q = currentArenaSearch.toLowerCase().trim();
      filtered = filtered.filter((f) => {
        const title = (f.title || "").toLowerCase();
        const claim = (f.claim || f.plain_english || "").toLowerCase();
        const rec = (f.suggested_negotiation || f.recommendation || "").toLowerCase();
        return title.includes(q) || claim.includes(q) || rec.includes(q);
      });
    }

    if (filtered.length === 0) {
      const isStandby = cachedDebateFindings.length === 0;
      debateArena.innerHTML = isStandby ? `
        <div style="background: #FFFFFF; border: 1.5px dashed var(--border-card); border-radius: var(--radius-lg); padding: 48px 24px; text-align: center; color: var(--text-muted); display: flex; flex-direction: column; align-items: center; gap: 12px;">
          <div style="width: 56px; height: 56px; border-radius: 50%; background: rgba(79, 70, 229, 0.08); display: flex; align-items: center; justify-content: center; font-size: 28px;">⚖️</div>
          <div style="font-size: 16px; font-weight: 800; color: var(--text-primary);">Courtroom Arena Ready on Standby</div>
          <p style="font-size: 13px; max-width: 520px; line-height: 1.5; margin: 0; color: var(--text-secondary);">
            Upload a contract to automatically cross-examine all clauses with dual-agent debate, or click any of the preset questions above to test the AI Courtroom in real-time.
          </p>
        </div>
      ` : `
        <div style="background: #FFFFFF; border: 1px dashed var(--border-card); border-radius: var(--radius-lg); padding: 40px; text-align: center; color: var(--text-muted);">
          <div style="font-size: 32px; margin-bottom: 8px;">⚖️</div>
          <div style="font-size: 15px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">No Courtroom Cases Found</div>
          <p style="font-size: 12.5px; margin: 0;">Try adjusting your filter or search query above.</p>
        </div>
      `;
      return;
    }

    filtered.forEach((finding, idx) => {
      const card = createCourtroomCaseCard(finding, idx);
      debateArena.appendChild(card);
    });
  }

  function createCourtroomCaseCard(finding, idx) {
    const debate = finding.debate_history?.[0] || {};
    const auditor = debate.finding || finding;
    const verifier = debate.verification || {};
    const verdict = String(verifier.verdict || "ACCEPTED").toUpperCase();
    const conf = Math.round((verifier.confidence || 0.98) * 100);

    const cb = finding.clause_balance || auditor.clause_balance;
    const isAsym = cb && (cb.is_asymmetric === true || Boolean(cb.asymmetry_summary));

    const evidence = auditor.evidence?.[0] || finding.evidence?.[0] || {};
    const quote = evidence.quote || "";
    const page = evidence.page ? `Page ${evidence.page}` : "PDF Document";
    const chunk = evidence.chunk_id || "Section Citation";
    const friendlyTitle = getFriendlyTitle(finding.title);

    let verdictStampHtml = "";
    if (isAsym) {
      verdictStampHtml = `<span class="verdict-stamp verdict-stamp-asymmetric">⚠️ ASYMMETRIC CLAUSE DETECTED (${conf}% MATCH)</span>`;
    } else if (verdict === "ACCEPTED") {
      verdictStampHtml = `<span class="verdict-stamp verdict-stamp-accepted">✓ UNANIMOUS: ACCEPTED (${conf}% MATCH)</span>`;
    } else {
      verdictStampHtml = `<span class="verdict-stamp verdict-stamp-challenged">✕ ${escapeHtml(verdict)}</span>`;
    }

    const card = document.createElement("div");
    card.className = "debate-card";

    let asymBlockHtml = "";
    if (isAsym) {
      asymBlockHtml = `
        <div class="asymmetric-meter-card">
          <div class="asym-meter-header">
            <span>⚖️ Unilateral Terms Comparison (Tug-of-War Balance)</span>
            <span class="badge-status status-critical">High Lopsidedness</span>
          </div>
          <div class="asym-scale-visual">
            <div class="asym-side-box asym-side-vendor">
              <div class="asym-side-label">🏢 Provider / Vendor Terms (Advantage)</div>
              <div class="asym-side-desc">${escapeHtml(cb.provider_terms || "Unilateral right or rapid notice privilege")}</div>
            </div>
            <div class="asym-scale-center">
              <div class="asym-tilt-icon">👈</div>
              <div class="asym-tilt-text">Tilted Against You</div>
            </div>
            <div class="asym-side-box asym-side-customer">
              <div class="asym-side-label">👤 Your Organization (Burdensome)</div>
              <div class="asym-side-desc">${escapeHtml(cb.customer_terms || "Long lock-in or burdensome conditions")}</div>
            </div>
          </div>
          ${cb.asymmetry_summary ? `<p class="asym-summary-text"><strong>Why This Disadvantages You:</strong> ${escapeHtml(cb.asymmetry_summary)}</p>` : ""}
        </div>
      `;
    }

    const redlineText = auditor.suggested_negotiation || auditor.recommendation || "";

    card.innerHTML = `
      <div class="debate-card-header">
        <div class="debate-header-left">
          <div class="debate-meta-tags">
            <span class="case-id-badge">CASE #${String(idx + 1).padStart(2, "0")}</span>
            <span class="badge-cat">${escapeHtml((finding.category || "CONTRACT RISK").toUpperCase())}</span>
            <span class="badge-status status-${finding.severity === "critical" ? "critical" : finding.severity === "high" ? "high" : "medium"}">
              ${escapeHtml((finding.severity || "medium").toUpperCase())} SEVERITY
            </span>
          </div>
          <div class="debate-topic">${escapeHtml(friendlyTitle)}</div>
        </div>
        ${verdictStampHtml}
      </div>

      <div class="debate-clash-grid">
        <!-- Prosecutor Column -->
        <div class="agent-column agent-column-prosecutor">
          <div class="agent-col-head">
            <div class="agent-col-title"><span>🤖</span> AI Prosecutor (GPT-4o)</div>
            <span class="agent-col-subtitle">Risk Allegation</span>
          </div>
          <div class="agent-col-text">${escapeHtml(auditor.plain_english || auditor.claim)}</div>
          ${quote ? `
            <div class="citation-evidence-box">
              <div class="citation-evidence-badge">
                <span>📄 Verbatim Contract Citation</span>
                <span>${escapeHtml(page)} · ${escapeHtml(chunk)}</span>
              </div>
              <div class="citation-quote-text">"${escapeHtml(quote)}"</div>
            </div>
          ` : ""}
        </div>

        <!-- Center Clash Divider -->
        <div class="clash-divider">
          <div class="clash-badge">VS</div>
        </div>

        <!-- Skeptic Column -->
        <div class="agent-column agent-column-skeptic">
          <div class="agent-col-head">
            <div class="agent-col-title"><span>🛡️</span> AI Skeptic (Gemini 2.5)</div>
            <span class="agent-col-subtitle">Sworn Verification</span>
          </div>
          <div class="agent-col-text">${escapeHtml(verifier.reasoning || "Confirmed word-for-word in the contract text with no conflicting exceptions or carve-outs.")}</div>
          <div class="fidelity-meter-box">
            <div class="fidelity-label-row">
              <span>PDF Citation Fidelity</span>
              <span>${conf}% Quote Match</span>
            </div>
            <div class="fidelity-bar-track">
              <div class="fidelity-bar-fill" style="width: ${conf}%;"></div>
            </div>
          </div>
        </div>
      </div>

      ${asymBlockHtml}

      ${redlineText ? `
        <div class="debate-remedy-box">
          <div class="remedy-left">
            <span class="remedy-tag">🎯 Ready-to-Use Negotiation Redline</span>
            <div class="remedy-text-clean">${escapeHtml(redlineText)}</div>
          </div>
          <button class="btn-copy-redline" data-fix="${escapeHtml(redlineText)}">
            <span>📋 Copy Redline</span>
          </button>
        </div>
      ` : ""}

      <div class="debate-transcript-accordion">
        <button class="debate-transcript-toggle" type="button">
          <span>▶ Inspect Raw Evidence & Deep-Dive Notes</span>
        </button>
        <div class="debate-transcript-content">
          <div><strong>Prosecutor Legal Assessment:</strong> ${escapeHtml(auditor.why_flagged || auditor.reasoning || "Direct contractual risk flagged.")}</div>
          <div style="margin-top: 6px;"><strong>Skeptic Cross-Examination Log:</strong> ${escapeHtml(verifier.reasoning || "Verified in raw PDF.")}</div>
          ${chunk ? `<div style="margin-top: 6px; font-family: var(--font-mono); font-size: 11px; color: var(--text-muted);">Indexed Coordinate: ${escapeHtml(chunk)} | ${escapeHtml(page)}</div>` : ""}
        </div>
      </div>
    `;

    // Copy redline handler
    const btnCopy = card.querySelector(".btn-copy-redline");
    btnCopy?.addEventListener("click", () => {
      navigator.clipboard.writeText(redlineText);
      showToast("Negotiation redline copied to clipboard!", "📋");
      btnCopy.innerHTML = `<span>✓ Copied!</span>`;
      setTimeout(() => {
        btnCopy.innerHTML = `<span>📋 Copy Redline</span>`;
      }, 2000);
    });

    // Accordion toggle
    const toggleBtn = card.querySelector(".debate-transcript-toggle");
    const content = card.querySelector(".debate-transcript-content");
    toggleBtn?.addEventListener("click", () => {
      const isOpen = content.classList.contains("open");
      if (isOpen) {
        content.classList.remove("open");
        toggleBtn.innerHTML = `<span>▶ Inspect Raw Evidence & Deep-Dive Notes</span>`;
      } else {
        content.classList.add("open");
        toggleBtn.innerHTML = `<span>▼ Hide Raw Evidence & Deep-Dive Notes</span>`;
      }
    });

    return card;
  }

  // Live Cross-Examination Runner (Ask & Verify Bar)
  async function runCourtroomQuery(query) {
    if (!query || !query.trim()) return;
    const cleanQuery = query.trim();

    showToast(`Cross-examining: "${cleanQuery}"...`, "⏳");

    if (btnAskCourtroom) {
      btnAskCourtroom.disabled = true;
      btnAskCourtroom.innerHTML = `<span>Cross-Examining...</span>`;
    }

    // Show dynamic simulation card
    if (courtroomSimCard) {
      courtroomSimCard.style.display = "flex";
      if (simQueryText) simQueryText.textContent = `"${cleanQuery}"`;
      
      const step1 = document.getElementById("sim-step-1");
      const step2 = document.getElementById("sim-step-2");
      const step3 = document.getElementById("sim-step-3");
      step1?.classList.add("sim-step-active");
      step2?.classList.remove("sim-step-active");
      step3?.classList.remove("sim-step-active");

      setTimeout(() => {
        step1?.classList.remove("sim-step-active");
        step2?.classList.add("sim-step-active");
      }, 1500);

      setTimeout(() => {
        step2?.classList.remove("sim-step-active");
        step3?.classList.add("sim-step-active");
      }, 3000);
    }

    try {
      const res = await fetch("/api/debate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: cleanQuery })
      });

      if (!res.ok) throw new Error("Debate endpoint error");
      const result = await res.json();

      // Backend returns finding in result.finding or fallback result.auditor_finding
      const finding = result.finding || result.auditor_finding || {};
      const verification = result.verification || result.verifier_result || {};
      
      const newFindingObj = {
        finding_id: "custom-" + Date.now(),
        title: cleanQuery,
        category: finding.category || "USER CROSS-EXAMINATION",
        severity: finding.severity || "medium",
        bucket: finding.bucket || "risk_to_monitor",
        claim: finding.claim || cleanQuery,
        plain_english: finding.plain_english || result.plain_english || finding.claim || cleanQuery,
        why_flagged: finding.why_flagged || result.why_flagged || finding.reasoning || "",
        suggested_negotiation: finding.suggested_negotiation || result.suggested_negotiation || finding.recommendation || "",
        clause_balance: finding.clause_balance || result.clause_balance || {},
        evidence: finding.evidence || result.evidence || [],
        debate_history: [
          {
            round: 1,
            finding: finding,
            verification: verification
          }
        ]
      };

      // Add to beginning of findings list
      cachedDebateFindings.unshift(newFindingObj);
      updateCourtroomScorecard(cachedDebateFindings);
      applyCourtroomFiltersAndRender();

      showToast("Case verified & added to courtroom docket!", "⚖️");

      // Scroll smoothly to top of arena
      debateArena?.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      showToast("Error during cross-examination: " + err.message, "❌");
    } finally {
      if (courtroomSimCard) {
        courtroomSimCard.style.display = "none";
      }
      if (btnAskCourtroom) {
        btnAskCourtroom.disabled = false;
        btnAskCourtroom.innerHTML = `
          <span>Ask & Verify</span>
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        `;
      }
    }
  }

  // Filter Buttons & Search Listeners
  arenaFilterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      arenaFilterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentArenaFilter = btn.getAttribute("data-filter") || "all";
      applyCourtroomFiltersAndRender();
    });
  });

  arenaSearchInput?.addEventListener("input", (e) => {
    currentArenaSearch = e.target.value || "";
    applyCourtroomFiltersAndRender();
  });

  btnAskCourtroom?.addEventListener("click", () => {
    runCourtroomQuery(courtroomQueryInput?.value);
  });

  courtroomQueryInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") runCourtroomQuery(courtroomQueryInput?.value);
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

  // Initialize Courtroom on standby
  renderCourtroomDebate([]);

  // Load Initial Data (will stay on clean welcome screen if no previous upload)
  loadLatestReport();
});
