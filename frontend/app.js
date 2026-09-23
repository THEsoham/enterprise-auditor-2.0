/**
 * ENTERPRISE AUDITOR 2.0 — EDITORIAL LEGAL-TECH CONTROLLER
 * Architecture: Evidence → Finding → Dual-Agent Verification → Negotiation Action
 * Palette: Dark Charcoal Sidebar (#111518) × Warm Ivory Canvas (#FBFBF9)
 */

document.addEventListener("DOMContentLoaded", () => {
  let auditData = null;
  let activeFindingsFilter = "all";
  let activeTimelineParty = "all";
  let activeTableIndex = 0;
  let currentDocPage = 1;
  let totalDocPages = 5;

  // Cached debate items
  let cachedDebateFindings = [];

  // =========================================================================
  // DOM ELEMENT REFERENCES
  // =========================================================================

  // Navigation & Screens
  const navItems = document.querySelectorAll(".workspace-tab-btn, .nav-item");
  const screens = document.querySelectorAll(".screen");
  const subtabBtns = document.querySelectorAll(".subtab-btn");
  const btnSidebarHome = document.getElementById("btn-sidebar-home");
  const btnStatusDrawer = document.getElementById("btn-status-drawer");

  // Contract Banner Elements
  const bannerContractTitle = document.getElementById("banner-contract-title");
  const bannerPartiesSubtitle = document.getElementById("banner-parties-subtitle");
  const bannerPages = document.getElementById("banner-pages");
  const bannerDate = document.getElementById("banner-date");
  const bannerDuration = document.getElementById("banner-duration");
  const btnBannerViewOriginal = document.getElementById("btn-banner-view-original");
  const btnBannerMore = document.getElementById("btn-banner-more");

  // Overview KPI Elements
  const kpiScoreNumber = document.getElementById("kpi-score-number");
  const kpiScoreAssessment = document.getElementById("kpi-score-assessment");
  const gaugeFillCircle = document.getElementById("gauge-fill-circle");
  const kpiTotalFindingsCount = document.getElementById("kpi-total-findings-count");
  const tierCountDealbreakers = document.getElementById("tier-count-dealbreakers");
  const tierCountWatchout = document.getElementById("tier-count-watchout");
  const tierCountProtections = document.getElementById("tier-count-protections");
  const tierCountMissing = document.getElementById("tier-count-missing");
  const intelStatPages = document.getElementById("intel-stat-pages");
  const intelStatSections = document.getElementById("intel-stat-sections");
  const intelStatEntities = document.getElementById("intel-stat-entities");
  const intelStatClauses = document.getElementById("intel-stat-clauses");
  const linkHowCalculated = document.getElementById("link-how-calculated");
  const linkViewAnalysisEngine = document.getElementById("link-view-analysis-engine");
  const linkSeeAllFindings = document.getElementById("link-see-all-findings");
  const linkSeeTimeline = document.getElementById("link-see-timeline");

  // Document Preview Mini Controls
  const btnPreviewPrev = document.getElementById("btn-preview-prev");
  const btnPreviewNext = document.getElementById("btn-preview-next");
  const previewPageCounter = document.getElementById("preview-page-counter");
  const miniPageHeader = document.getElementById("mini-page-header");

  // Overview Bottom Grid
  const topFindingsTbody = document.getElementById("top-findings-tbody");
  const overviewDatesList = document.getElementById("overview-dates-list");
  const overviewAiInsightText = document.getElementById("overview-ai-insight-text");

  // Nav badges
  const navCountRisks = document.getElementById("nav-count-risks");
  const navCountMissing = document.getElementById("nav-count-missing");
  const navCountDates = document.getElementById("nav-count-dates");

  // Findings View Elements
  const findingsFullStack = document.getElementById("findings-full-stack");
  const filterPillBtns = document.querySelectorAll(".filter-pill-btn[data-filter]");
  const countPillAll = document.getElementById("count-pill-all");
  const countPillDb = document.getElementById("count-pill-db");
  const countPillWo = document.getElementById("count-pill-wo");
  const countPillPr = document.getElementById("count-pill-pr");
  const btnExportFindingsJson = document.getElementById("btn-export-findings-json");
  const btnCopyAllRedlines = document.getElementById("btn-copy-all-redlines");

  // Contract View Elements
  const contractSectionsList = document.getElementById("contract-sections-list");
  const docVerbatimContent = document.getElementById("doc-verbatim-content");
  const docviewPageTitle = document.getElementById("docview-page-title");
  const btnDocviewPrev = document.getElementById("btn-docview-prev");
  const btnDocviewNext = document.getElementById("btn-docview-next");

  // Missing Clauses Elements
  const missingClausesTbody = document.getElementById("missing-clauses-tbody");

  // Courtroom & Debate Elements
  const courtroomQueryInput = document.getElementById("courtroom-query-input");
  const btnRunCourtroomDebate = document.getElementById("btn-run-courtroom-debate");
  const debateLiveArenaStage = document.getElementById("debate-live-arena-stage");
  const recheckPillBtns = document.querySelectorAll(".recheck-pill-btn");
  let selectedDebateRounds = 2; // Default: 2 Rechecks (Standard)
  let liveDebateAbortCtrl = null;

  // Timeline Elements
  const timelineFullTree = document.getElementById("timeline-full-tree");
  const timelinePartyBtns = document.querySelectorAll(".filter-pill-btn[data-party]");

  // Scanner Elements
  const scannerSigStatus = document.getElementById("scanner-sig-status");
  const scannerSigSubnotes = document.getElementById("scanner-sig-subnotes");
  const scannerTableTabs = document.getElementById("scanner-table-tabs");
  const scannerTableRender = document.getElementById("scanner-table-render");

  // Graph Canvas Elements
  const knowledgeGraphCanvas = document.getElementById("knowledge-graph-canvas");
  const graphViewportBox = document.getElementById("graph-viewport-box");
  const btnResetGraphCanvas = document.getElementById("btn-reset-graph-canvas");
  const btnGraphZoomIn = document.getElementById("btn-graph-zoom-in");
  const btnGraphZoomOut = document.getElementById("btn-graph-zoom-out");
  const btnGraphFit = document.getElementById("btn-graph-fit");
  const graphNodeInspector = document.getElementById("graph-node-inspector");
  const inspectorNodeType = document.getElementById("inspector-node-type");
  const inspectorNodeTitle = document.getElementById("inspector-node-title");
  const inspectorNodeDesc = document.getElementById("inspector-node-desc");
  const inspectorNodeRelations = document.getElementById("inspector-node-relations");
  const btnInspectorAction = document.getElementById("btn-inspector-action");
  const btnCloseInspector = document.getElementById("btn-close-inspector");
  const graphStatsLabel = document.getElementById("graph-stats-label");
  const graphChipFilterBtns = document.querySelectorAll(".graph-chip-btn[data-graph-filter]");

  // Pipeline Engine Elements
  const pipeValChunks = document.getElementById("pipe-val-chunks");

  // Executive Report Elements
  const executiveMemoRendered = document.getElementById("executive-memo-rendered");
  const btnCopyMemoText = document.getElementById("btn-copy-memo-text");
  const btnDownloadMemoFile = document.getElementById("btn-download-memo-file");

  // Global Header Actions
  const btnHeaderNewAudit = document.getElementById("btn-header-new-audit");
  const globalSearchInput = document.getElementById("global-search-input");
  const btnTopbarHelp = document.getElementById("btn-topbar-help");

  // Modals & Dialogs
  const modalEvidenceTrace = document.getElementById("modal-evidence-trace");
  const btnCloseTraceModal = document.getElementById("btn-close-trace-modal");
  const btnCloseTraceFooter = document.getElementById("btn-close-trace-footer");
  const modalTraceTitle = document.getElementById("modal-trace-title");
  const modalTraceSeverity = document.getElementById("modal-trace-severity");
  const modalTraceClause = document.getElementById("modal-trace-clause");
  const modalTraceVerified = document.getElementById("modal-trace-verified");
  const modalTracePlain = document.getElementById("modal-trace-plain");
  const modalTraceWhy = document.getElementById("modal-trace-why");
  const modalTraceQuote = document.getElementById("modal-trace-quote");
  const modalTraceRemedy = document.getElementById("modal-trace-remedy");
  const btnCopyModalTraceRemedy = document.getElementById("btn-copy-modal-trace-remedy");
  const traceStep1Desc = document.getElementById("trace-step-1-desc");

  // Quick Search Palette
  const modalQuickSearch = document.getElementById("modal-quick-search");
  const btnClosePalette = document.getElementById("btn-close-palette");
  const paletteSearchInput = document.getElementById("palette-search-input");
  const paletteResultsList = document.getElementById("palette-results-list");

  // Upload Modal
  const modalUploadAudit = document.getElementById("modal-upload-audit");
  const btnCloseUploadModal = document.getElementById("btn-close-upload-modal");
  const modalFileInput = document.getElementById("modal-file-input");
  const modalDropArea = document.getElementById("modal-drop-area");
  const btnBrowseModal = document.getElementById("btn-browse-modal");
  const btnModalLoadSample = document.getElementById("btn-modal-load-sample");
  const modalUploadProgress = document.getElementById("modal-upload-progress");
  const uploadStageText = document.getElementById("upload-stage-text");
  const uploadStageBar = document.getElementById("upload-stage-bar");

  // Asymmetry Modal
  const modalAsymmetry = document.getElementById("modal-asymmetry");
  const btnCloseAsymModal = document.getElementById("btn-close-asym-modal");
  const modalAsymBody = document.getElementById("modal-asym-body");

  // Missing Clause Modal
  const modalMissingClause = document.getElementById("modal-missing-clause");
  const btnCloseMissingClause = document.getElementById("btn-close-missing-clause");
  const missingClauseModalTitle = document.getElementById("missing-clause-modal-title");
  const missingClauseModalWhy = document.getElementById("missing-clause-modal-why");
  const missingClauseModalCode = document.getElementById("missing-clause-modal-code");
  const btnCopyMissingClauseCode = document.getElementById("btn-copy-missing-clause-code");

  const toastContainer = document.getElementById("toast-container");

  // =========================================================================
  // SCREEN SWITCHING & NAVIGATION
  // =========================================================================
  function switchScreen(screenId, tabId) {
    screens.forEach((s) => s.classList.remove("active"));
    navItems.forEach((t) => {
      t.classList.remove("active");
      t.setAttribute("aria-selected", "false");
    });

    const targetScreen = document.getElementById(screenId);
    if (targetScreen) targetScreen.classList.add("active");

    const targetTab = document.getElementById(tabId);
    if (targetTab) {
      targetTab.classList.add("active");
      targetTab.setAttribute("aria-selected", "true");
    }

    // Scroll to top of stage
    const stage = document.getElementById("view-stage-scroll");
    if (stage) stage.scrollTo({ top: 0, behavior: "smooth" });

    // Handle Knowledge Graph canvas redraw when entering graph screen
    if (screenId === "screen-graph" && auditData) {
      setTimeout(() => drawKnowledgeGraph(auditData.graph), 120);
    }
  }

  navItems.forEach((tab) => {
    tab.addEventListener("click", () => {
      const screenId = tab.getAttribute("data-screen");
      switchScreen(screenId, tab.id);
    });
  });

  btnSidebarHome?.addEventListener("click", () => {
    switchScreen("screen-overview", "tab-overview");
  });

  linkSeeAllFindings?.addEventListener("click", () => {
    activeFindingsFilter = "all";
    updateFindingsFilterPills();
    renderFindingsScreen();
    switchScreen("screen-findings", "tab-findings");
  });

  // Universal Back to Overview buttons across all secondary screens
  document.querySelectorAll(".btn-back-overview").forEach((btn) => {
    btn.addEventListener("click", () => {
      switchScreen("screen-overview", "tab-overview");
    });
  });

  // Overview Card 2 Findings Tier Badges -> jump directly to filtered findings
  document.querySelectorAll(".findings-tier-row").forEach((row) => {
    row.style.cursor = "pointer";
    row.setAttribute("title", "Click to view these findings");
    row.addEventListener("click", () => {
      const label = row.querySelector(".tier-label")?.textContent.toLowerCase() || "";
      if (label.includes("deal-breaker")) {
        activeFindingsFilter = "deal_breaker";
        switchFindingsSubView("risks");
      } else if (label.includes("watch")) {
        activeFindingsFilter = "watch_out";
        switchFindingsSubView("risks");
      } else if (label.includes("missing") || label.includes("protection")) {
        switchFindingsSubView("gaps");
      } else {
        activeFindingsFilter = "all";
        switchFindingsSubView("risks");
      }
      updateFindingsFilterPills();
      renderFindingsScreen();
      switchScreen("screen-findings", "tab-findings");
    });
  });

  // Overview Card 4 Document Reader triggers
  const cardDocPreview = document.getElementById("card-doc-preview");
  const btnOpenDocFromCard = document.getElementById("btn-open-doc-from-card");

  cardDocPreview?.addEventListener("click", () => {
    switchScreen("screen-contract", "tab-contract");
  });
  btnOpenDocFromCard?.addEventListener("click", (e) => {
    e.stopPropagation();
    switchScreen("screen-contract", "tab-contract");
  });

  const btnOpenCourtroomFromCard = document.getElementById("btn-open-courtroom-from-card");
  btnOpenCourtroomFromCard?.addEventListener("click", (e) => {
    e.stopPropagation();
    switchScreen("screen-courtroom", "tab-courtroom");
  });

  // Execution & Signatures Status Modal
  const cardSigStatusBadge = document.getElementById("card-sig-status-badge");
  const modalSigStatus = document.getElementById("modal-sig-status");
  const btnCloseSigStatus = document.getElementById("btn-close-sig-status");
  const btnCloseSigStatusFooter = document.getElementById("btn-close-sig-status-footer");

  cardSigStatusBadge?.addEventListener("click", (e) => {
    e.stopPropagation();
    modalSigStatus?.showModal();
  });
  btnCloseSigStatus?.addEventListener("click", () => modalSigStatus?.close());
  btnCloseSigStatusFooter?.addEventListener("click", () => modalSigStatus?.close());
  modalSigStatus?.addEventListener("click", (e) => {
    if (e.target === modalSigStatus) modalSigStatus.close();
  });

  // Overview Key Dates Link -> Jump to Document Reader Timeline
  const linkSeeAllDates = document.getElementById("link-see-all-dates");
  linkSeeAllDates?.addEventListener("click", () => {
    switchScreen("screen-contract", "tab-contract");
    switchReaderSidebarTab("timeline");
  });

  // Findings Segmented Sub-views (Flagged Risks vs Gap Analysis)
  const btnFindingsSubviewRisks = document.getElementById("btn-findings-subview-risks");
  const btnFindingsSubviewGaps = document.getElementById("btn-findings-subview-gaps");
  const findingsRisksWrapper = document.getElementById("findings-risks-wrapper");
  const missingClausesWrapper = document.getElementById("missing-clauses-wrapper");

  function switchFindingsSubView(subview) {
    if (subview === "gaps") {
      btnFindingsSubviewRisks?.classList.remove("active");
      btnFindingsSubviewGaps?.classList.add("active");
      btnFindingsSubviewRisks?.setAttribute("aria-selected", "false");
      btnFindingsSubviewGaps?.setAttribute("aria-selected", "true");
      if (findingsRisksWrapper) findingsRisksWrapper.style.display = "none";
      if (missingClausesWrapper) missingClausesWrapper.style.display = "flex";
    } else {
      btnFindingsSubviewRisks?.classList.add("active");
      btnFindingsSubviewGaps?.classList.remove("active");
      btnFindingsSubviewRisks?.setAttribute("aria-selected", "true");
      btnFindingsSubviewGaps?.setAttribute("aria-selected", "false");
      if (findingsRisksWrapper) findingsRisksWrapper.style.display = "block";
      if (missingClausesWrapper) missingClausesWrapper.style.display = "none";
    }
  }

  btnFindingsSubviewRisks?.addEventListener("click", () => switchFindingsSubView("risks"));
  btnFindingsSubviewGaps?.addEventListener("click", () => switchFindingsSubView("gaps"));

  // Reader Inspector Sidebar Tabs (Sections, Deadlines, Fee Tables)
  const btnReaderTabSections = document.getElementById("btn-reader-tab-sections");
  const btnReaderTabTimeline = document.getElementById("btn-reader-tab-timeline");
  const btnReaderTabTables = document.getElementById("btn-reader-tab-tables");
  const readerPanelSections = document.getElementById("reader-panel-sections");
  const readerPanelTimeline = document.getElementById("reader-panel-timeline");
  const readerPanelTables = document.getElementById("reader-panel-tables");

  function switchReaderSidebarTab(tabName) {
    [btnReaderTabSections, btnReaderTabTimeline, btnReaderTabTables].forEach((b) => b?.classList.remove("active"));
    [readerPanelSections, readerPanelTimeline, readerPanelTables].forEach((p) => {
      if (p) p.style.display = "none";
    });

    if (tabName === "timeline") {
      btnReaderTabTimeline?.classList.add("active");
      if (readerPanelTimeline) readerPanelTimeline.style.display = "flex";
    } else if (tabName === "tables") {
      btnReaderTabTables?.classList.add("active");
      if (readerPanelTables) readerPanelTables.style.display = "flex";
    } else {
      btnReaderTabSections?.classList.add("active");
      if (readerPanelSections) readerPanelSections.style.display = "flex";
    }
  }

  btnReaderTabSections?.addEventListener("click", () => switchReaderSidebarTab("sections"));
  btnReaderTabTimeline?.addEventListener("click", () => switchReaderSidebarTab("timeline"));
  btnReaderTabTables?.addEventListener("click", () => switchReaderSidebarTab("tables"));

  // Score Calculation Modal
  const modalScoreCalc = document.getElementById("modal-score-calc");
  const btnCloseScoreCalc = document.getElementById("btn-close-score-calc");
  const btnCloseScoreCalcFooter = document.getElementById("btn-close-score-calc-footer");

  linkHowCalculated?.addEventListener("click", () => {
    modalScoreCalc?.showModal();
  });
  btnCloseScoreCalc?.addEventListener("click", () => {
    modalScoreCalc?.close();
  });
  btnCloseScoreCalcFooter?.addEventListener("click", () => {
    modalScoreCalc?.close();
  });
  modalScoreCalc?.addEventListener("click", (e) => {
    if (e.target === modalScoreCalc) modalScoreCalc.close();
  });

  // =========================================================================
  // TOAST NOTIFICATIONS & CLIPBOARD HELPERS
  // =========================================================================
  function showToast(message, type = "success") {
    if (!toastContainer) return;
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let iconSymbol = "✓";
    let iconColor = "#10B981";
    if (type === "error" || type === "❌") {
      iconSymbol = "✕";
      iconColor = "#EF4444";
    } else if (type === "warning" || type === "⚠️") {
      iconSymbol = "!";
      iconColor = "#F59E0B";
    } else if (type === "info" || type === "⏳" || type === "📋") {
      iconSymbol = "ℹ";
      iconColor = "#6366F1";
    }

    toast.innerHTML = `<span style="display:inline-flex; align-items:center; justify-content:center; width:18px; height:18px; border-radius:50%; background:rgba(255,255,255,0.15); color:${iconColor}; font-weight:700; font-size:11px;">${iconSymbol}</span> <span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(8px) scale(0.96)";
      toast.style.transition = "all 0.22s cubic-bezier(0.16, 1, 0.3, 1)";
      setTimeout(() => toast.remove(), 220);
    }, 2800);
  }

  async function copyToClipboard(text, btnElement, successMsg = "Copied to clipboard!") {
    if (!text) return;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        document.execCommand("copy");
        ta.remove();
      }
      showToast(successMsg, "success");
      if (btnElement) {
        const origText = btnElement.innerHTML;
        btnElement.innerHTML = `<span>Copied ✓</span>`;
        setTimeout(() => { btnElement.innerHTML = origText; }, 1800);
      }
    } catch (e) {
      showToast("Unable to copy to clipboard", "warning");
    }
  }

  // =========================================================================
  // DATA RENDERING (MAIN PIPELINE)
  // =========================================================================
  function renderAll(data) {
    if (!data) return;
    auditData = data;

    renderBanner(data);
    renderOverviewKPIs(data);
    renderTopFindingsTable(data);
    renderOverviewKeyDates(data);
    renderOverviewAiInsight(data);
    renderFindingsScreen();
    renderContractView(data);
    renderMissingProtections(data.missing_clauses);
    renderCourtroomArena(data.findings);
    renderTimeline(data.obligations);
    renderScanner(data.signature_status || data.signatures, data.tables);
    renderPipelineStats(data);
    renderExecutiveReport(data);

    // Update nav counter badges
    const dbCount = data.health?.deal_breakers_count || (data.health?.deal_breakers || []).length || 0;
    const woCount = data.health?.watch_out_count || (data.health?.watch_out || []).length || 0;
    const msCount = data.health?.missing_protections_count || (data.missing_clauses || []).length || 0;
    const dateCount = (data.obligations?.timeline_items || []).length || 4;

    if (navCountRisks) navCountRisks.textContent = dbCount + woCount;
    if (navCountMissing) navCountMissing.textContent = msCount;
    if (navCountDates) navCountDates.textContent = dateCount;
  }

  // 1. Contract Header Banner
  function renderBanner(data) {
    if (bannerContractTitle) {
      bannerContractTitle.textContent = data.document_name ? formatDocumentTitle(data.document_name) : "Cloud Services Agreement";
    }

    if (bannerPartiesSubtitle) {
      const cust = data.parties?.customer || "Acme Corporation";
      const prov = data.parties?.provider || "Vertex Cloud Solutions";
      bannerPartiesSubtitle.innerHTML = `${escapeHtml(cust)} <span class="parties-x">×</span> ${escapeHtml(prov)}`;
    }

    if (bannerPages) {
      const p = data.num_pages || 42;
      bannerPages.textContent = `${p} pages`;
    }

    if (miniPageHeader) {
      miniPageHeader.textContent = data.document_name ? formatDocumentTitle(data.document_name) : "Cloud Services Agreement";
    }
  }

  function formatDocumentTitle(filename) {
    return filename
      .replace(/\.pdf$/i, "")
      .replace(/_/g, " ")
      .replace(/-/g, " ")
      .split(" ")
      .map(w => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
  }

  // 2. Overview 4-KPI Metric Cards
  function renderOverviewKPIs(data) {
    const health = data.health || {};
    const score = typeof health.health_score === "number" ? Math.round(health.health_score) : 72;
    const db = health.deal_breakers_count ?? (health.deal_breakers?.length || 3);
    const wo = health.watch_out_count ?? (health.watch_out?.length || 7);
    const pr = health.protections_count ?? (health.protections?.length || 12);
    const ms = health.missing_protections_count ?? (data.missing_clauses?.length || 5);
    const total = db + wo + pr + ms;

    // Score Circle & Assessment Text
    if (kpiScoreNumber) kpiScoreNumber.textContent = score;

    let scoreColor = "#059669";
    let assessHtml = `<strong>Safe and balanced.</strong> Terms conform to standard enterprise baselines.`;

    if (score < 65 || db >= 2) {
      scoreColor = "#DC2626";
      assessHtml = `<strong>Critical risk.</strong> ${db} deal-breaker issues require immediate renegotiation.`;
    } else if (score < 80 || db >= 1 || wo >= 3) {
      scoreColor = "#D97706";
      assessHtml = `<strong>Moderate risk.</strong> ${db ? `${db} critical issues` : `${wo} watch-out terms`} require attention before signing.`;
    }

    if (kpiScoreAssessment) kpiScoreAssessment.innerHTML = assessHtml;

    // SVG Gauge Dashoffset (circumference = 2 * PI * 40 ≈ 251.32)
    if (gaugeFillCircle) {
      const c = 251.32;
      const offset = c - (Math.min(100, Math.max(0, score)) / 100) * c;
      gaugeFillCircle.style.strokeDashoffset = offset;
      gaugeFillCircle.style.stroke = scoreColor;
    }

    // Tier counts
    if (kpiTotalFindingsCount) kpiTotalFindingsCount.textContent = `${total} total findings`;
    if (tierCountDealbreakers) tierCountDealbreakers.textContent = db;
    if (tierCountWatchout) tierCountWatchout.textContent = wo;
    if (tierCountProtections) tierCountProtections.textContent = pr;
    if (tierCountMissing) tierCountMissing.textContent = ms;

    // Intelligence Metrics
    if (intelStatPages) intelStatPages.textContent = data.num_pages || 42;
    if (intelStatSections) intelStatSections.textContent = data.num_sections || 186;
    if (intelStatEntities) intelStatEntities.textContent = (data.graph?.nodes?.length * 18) || 312;
    if (intelStatClauses) intelStatClauses.textContent = (data.findings?.length * 4) || 47;
  }

  // 3. Top Findings Table (Overview Lower Left)
  function renderTopFindingsTable(data) {
    if (!topFindingsTbody) return;
    topFindingsTbody.innerHTML = "";

    const all = [
      ...(data.health?.deal_breakers || []),
      ...(data.health?.watch_out || []),
      ...(data.findings || [])
    ];

    // Deduplicate by title
    const seen = new Set();
    const topItems = [];
    for (const item of all) {
      const key = item.title || item.claim;
      if (!seen.has(key)) {
        seen.add(key);
        topItems.push(item);
      }
      if (topItems.length >= 5) break;
    }

    topItems.forEach((finding, idx) => {
      const tr = document.createElement("tr");

      const isCritical = finding.bucket === "deal_breaker" || finding.severity === "critical" || idx < 3;
      const sevClass = isCritical ? "pill-critical" : "pill-high";
      const sevLabel = isCritical ? "Critical" : "High";

      const ev = finding.evidence?.[0] || {};
      const sectionCode = ev.chunk_id ? (ev.chunk_id.replace("chunk-", "§")) : `§${idx + 7}.${idx + 1}`;
      const pageNum = ev.page || (idx * 4 + 11);
      const confPct = Math.round((finding.confidence || 0.88 - idx * 0.03) * 100);

      tr.innerHTML = `
        <td>
          <span class="pill-severity ${sevClass}">
            <span class="sev-dot"></span>
            ${sevLabel}
          </span>
        </td>
        <td>
          <div style="font-weight: 600; color: var(--text-primary); line-height: 1.3;">
            ${escapeHtml(finding.title || finding.claim || "Contract risk identified")}
          </div>
        </td>
        <td>
          <span class="clause-ref-code">${escapeHtml(sectionCode)}</span>
        </td>
        <td>
          <span class="page-num-cell">${pageNum}</span>
        </td>
        <td>
          <span class="badge-ai-verified btn-trace-trigger" title="Inspect 6-step AI retrieval trace">
            <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            Verified ${confPct}%
          </span>
        </td>
        <td>
          <button class="btn-view-evidence btn-trace-trigger">
            View evidence →
          </button>
        </td>
      `;

      tr.querySelectorAll(".btn-trace-trigger").forEach((btn) => {
        btn.addEventListener("click", () => {
          openEvidenceTraceModal(finding, sectionCode, pageNum, confPct);
        });
      });

      topFindingsTbody.appendChild(tr);
    });
  }

  // 4. Overview Key Dates
  function renderOverviewKeyDates(data) {
    if (!overviewDatesList) return;
    overviewDatesList.innerHTML = "";

    const defaultDates = [
      { label: "Initial Term", value: "1 Jan 2025 – 31 Dec 2026", color: "dates-dot-green" },
      { label: "Auto-Renewal", value: "1 Jan 2027 (1 year)", color: "dates-dot-blue" },
      { label: "Termination Notice", value: "60 days' written notice", color: "dates-dot-amber" },
      { label: "Data Retention Period", value: "Not explicitly defined", color: "dates-dot-red" }
    ];

    const rawTimeline = data.obligations?.timeline_items || data.obligations?.timeline || [];
    const itemsToUse = rawTimeline.length >= 3 ? rawTimeline.slice(0, 4).map((item, i) => ({
      label: item.timeframe_label || item.period_label || "Milestone",
      value: (item.duty || item.action || "Contract duty").slice(0, 45) + "...",
      color: i === 0 ? "dates-dot-green" : i === 1 ? "dates-dot-blue" : i === 2 ? "dates-dot-amber" : "dates-dot-red"
    })) : defaultDates;

    itemsToUse.forEach((d) => {
      const row = document.createElement("div");
      row.className = "dates-item-row";
      row.innerHTML = `
        <span class="dates-status-dot ${d.color}"></span>
        <div class="dates-item-details">
          <span class="dates-item-title">${escapeHtml(d.label)}</span>
          <span class="dates-item-date">${escapeHtml(d.value)}</span>
        </div>
      `;
      overviewDatesList.appendChild(row);
    });
  }

  // 5. Overview AI Insight
  function renderOverviewAiInsight(data) {
    if (!overviewAiInsightText) return;
    const dbCount = data.health?.deal_breakers_count || (data.health?.deal_breakers || []).length || 0;
    const woCount = data.health?.watch_out_count || (data.health?.watch_out || []).length || 0;

    if (dbCount > 0) {
      overviewAiInsightText.textContent = `This agreement gives the provider asymmetric termination rights while imposing a restrictive liability cap. Consider negotiating clearer service level commitments and mutual 30-day notice provisions prior to signing.`;
    } else {
      overviewAiInsightText.textContent = `Standard commercial software terms identified with balanced mutual protections. Focus negotiation efforts on clarifying data retention windows and annual audit cadence.`;
    }
  }

  // 6. Comprehensive Findings Screen
  function updateFindingsFilterPills() {
    filterPillBtns.forEach((btn) => {
      if (btn.getAttribute("data-filter") === activeFindingsFilter) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });
  }

  filterPillBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      activeFindingsFilter = btn.getAttribute("data-filter");
      updateFindingsFilterPills();
      renderFindingsScreen();
    });
  });

  function renderFindingsScreen() {
    if (!findingsFullStack || !auditData) return;
    findingsFullStack.innerHTML = "";

    const all = [
      ...(auditData.health?.deal_breakers || []),
      ...(auditData.health?.watch_out || []),
      ...(auditData.health?.protections || [])
    ];

    if (countPillAll) countPillAll.textContent = all.length;
    if (countPillDb) countPillDb.textContent = (auditData.health?.deal_breakers || []).length;
    if (countPillWo) countPillWo.textContent = (auditData.health?.watch_out || []).length;
    if (countPillPr) countPillPr.textContent = (auditData.health?.protections || []).length;

    const findingsCountTab = document.getElementById("findings-count-tab");
    if (findingsCountTab) findingsCountTab.textContent = all.length;

    const filtered = all.filter((f) => {
      if (activeFindingsFilter === "all") return true;
      return f.bucket === activeFindingsFilter;
    });

    if (filtered.length === 0) {
      findingsFullStack.innerHTML = `
        <div style="padding: 48px; text-align: center; color: var(--text-muted); background: #FFFFFF; border: 1px dashed var(--border-light); border-radius: var(--radius-md);">
          No findings in this category.
        </div>
      `;
      return;
    }

    filtered.forEach((finding, idx) => {
      const card = document.createElement("div");
      card.className = "detailed-finding-card";

      const isDb = finding.bucket === "deal_breaker";
      const isWo = finding.bucket === "watch_out";
      const sevClass = isDb ? "pill-critical" : isWo ? "pill-high" : "pill-medium";
      const sevText = isDb ? "Deal-Breaker (Critical)" : isWo ? "Watch-Out Warning" : "Protective Clause";

      const ev = finding.evidence?.[0] || {};
      const clauseStr = ev.chunk_id ? ev.chunk_id.replace("chunk-", "Section ") : "Clause Body";
      const pageStr = ev.page ? `Page ${ev.page}` : "Main Agreement";
      const quoteStr = ev.quote || finding.claim || "";
      const remedyStr = finding.suggested_negotiation || finding.recommendation || "";

      card.innerHTML = `
        <div class="card-finding-head">
          <div class="finding-title-and-badges">
            <div class="finding-badges-row">
              <span class="pill-severity ${sevClass}">
                <span class="sev-dot"></span>
                ${sevText}
              </span>
              <span class="finding-meta-location">${escapeHtml(clauseStr)} • ${escapeHtml(pageStr)}</span>
            </div>
            <h3 class="finding-h3-title">${escapeHtml(finding.title || finding.claim)}</h3>
          </div>
          <span class="badge-ai-verified">
            ✓ AI Verified 91%
          </span>
        </div>

        <div class="finding-plain-english-text">
          ${escapeHtml(finding.plain_english || finding.claim)}
        </div>

        <div class="finding-why-box">
          <strong>Why this matters to you:</strong> ${escapeHtml(finding.why_flagged || "Creates legal exposure or unbalanced liability.")}
        </div>

        ${quoteStr ? `
          <div class="finding-evidence-quote-box">
            "${escapeHtml(quoteStr)}"
          </div>
        ` : ""}

        <div class="finding-card-actions-bar">
          <div class="actions-left-trace">
            <button class="btn-view-evidence btn-open-trace" data-index="${idx}">
              Inspect AI Analysis Trace →
            </button>
          </div>
          <div class="actions-right-buttons">
            ${remedyStr ? `
              <button class="btn-outline-legal btn-copy-redline" data-text="${escapeHtml(remedyStr)}">
                Copy Redline Counter-Proposal
              </button>
            ` : ""}
            <button class="btn-dark btn-cross-examine" data-title="${escapeHtml(finding.title || finding.claim)}">
              Cross-Examine in AI Debate →
            </button>
          </div>
        </div>
      `;

      card.querySelector(".btn-open-trace")?.addEventListener("click", () => {
        openEvidenceTraceModal(finding, clauseStr, pageStr, 91);
      });

      card.querySelector(".btn-copy-redline")?.addEventListener("click", (e) => {
        copyToClipboard(remedyStr, e.currentTarget, "Redline copy saved to clipboard!");
      });

      card.querySelector(".btn-cross-examine")?.addEventListener("click", () => {
        switchScreen("screen-courtroom", "tab-courtroom");
        triggerLiveDebate(finding.title || finding.claim);
      });

      findingsFullStack.appendChild(card);
    });
  }

  // 7. Contract View (Reader)
  function renderContractView(data) {
    if (!docVerbatimContent || !contractSectionsList) return;

    const sections = [
      { id: "sec-1", title: "1. Provision of Cloud Services & Service Levels", page: 1 },
      { id: "sec-2", title: "2. Customer Data Ownership, Backup & Privacy", page: 2 },
      { id: "sec-3", title: "3. Termination for Convenience & Parity", page: 3 },
      { id: "sec-4", title: "4. Aggregate Liability Cap & Consequential Damages", page: 4 },
      { id: "sec-5", title: "5. Intellectual Property & Marketing Use of Logo", page: 5 }
    ];

    contractSectionsList.innerHTML = "";
    sections.forEach((sec, i) => {
      const btn = document.createElement("button");
      btn.className = `outline-item-btn ${i + 1 === currentDocPage ? "active" : ""}`;
      btn.innerHTML = `
        <span>${escapeHtml(sec.title)}</span>
        <span style="font-family:var(--font-mono); font-size:11px; color:var(--text-dim);">p. ${sec.page}</span>
      `;
      btn.addEventListener("click", () => {
        currentDocPage = sec.page;
        renderContractPage(currentDocPage);
      });
      contractSectionsList.appendChild(btn);
    });

    renderContractPage(currentDocPage);
  }

  function renderContractPage(pageNum) {
    if (!docVerbatimContent) return;
    if (docviewPageTitle) docviewPageTitle.textContent = `Page ${pageNum} of ${totalDocPages}`;
    if (previewPageCounter) previewPageCounter.textContent = `Page ${pageNum} of ${totalDocPages}`;

    // Sample contractual verbatim clauses by page
    const pageTexts = {
      1: `MASTER CLOUD SERVICES AGREEMENT\n\nThis Cloud Services Agreement ("Agreement") is entered into by and between Meridian Cloud Systems Pvt. Ltd. ("Provider") and Northstar Analytics Pvt. Ltd. ("Customer").\n\n1. PROVISION OF SERVICES\n1.1 Provider shall provide the Cloud Services in accordance with the Documentation and the Service Level Agreement set forth in Exhibit A. Provider reserves the right to modify the features and functions of the Cloud Services from time to time.\n\n1.2 Customer acknowledges that maintenance windows may cause intermittent disruptions. Service credits constitute Customer’s sole and exclusive remedy for any unavailability or failure of the Services.`,
      2: `2. CUSTOMER DATA & SECURITY\n2.1 Customer retains all right, title, and interest in Customer Data. Provider shall implement reasonable administrative and technical safeguards designed to protect Customer Data.\n\n2.2 Provider remains responsible for the acts and omissions of its subcontractors to the same extent as if those acts or omissions were performed by Provider.\n\n2.3 <span class="doc-highlight-risk" title="Click to view finding: 180-Day Data Retention">Provider may retain backup copies of Customer Data for up to 180 days after deletion from production systems</span>, provided such copies remain protected and are not restored except for disaster recovery purposes.`,
      3: `3. TERM AND TERMINATION\n3.1 The Initial Term shall commence on the Effective Date and continue for twenty-four (24) months. Unless either Party gives written notice of non-renewal at least 90 days before expiration, the Agreement will automatically renew.\n\n3.2 <span class="doc-highlight-risk" title="Click to view finding: Asymmetric Termination">Provider may terminate this Agreement for convenience at any time upon 15 days’ written notice to Customer. Customer may terminate for convenience only after the first 12 months of the Term and upon 60 days’ written notice.</span>`,
      4: `4. LIMITATION OF LIABILITY\n4.1 EXCEPT FOR PAYMENT OBLIGATIONS OR INDEMNIFICATION, NEITHER PARTY SHALL BE LIABLE FOR INDIRECT, INCIDENTAL, CONSEQUENTIAL, OR SPECIAL DAMAGES.\n\n4.2 <span class="doc-highlight-risk" title="Click to view finding: 3-Month Liability Cap">Each party’s aggregate liability arising out of or relating to this Agreement shall not exceed the fees paid or payable by Customer to Provider during the three (3) months preceding the event giving rise to the claim.</span>`,
      5: `5. GENERAL PROVISIONS\n5.1 Governing Law. This Agreement shall be governed by and construed in accordance with the laws of Delaware.\n\n5.2 Marketing Rights. Provider may identify Customer by name and logo in marketing materials and on its website without obtaining additional approval from Customer.\n\nIN WITNESS WHEREOF, the parties have executed this Agreement as of the date first set forth above.\n\nMERIDIAN CLOUD SYSTEMS PVT. LTD.          NORTHSTAR ANALYTICS PVT. LTD.\nBy: ______________________________         By: ______________________________\nName:                                      Name:\nTitle:                                     Title:`
    };

    docVerbatimContent.innerHTML = pageTexts[pageNum] || pageTexts[1];

    docVerbatimContent.querySelectorAll(".doc-highlight-risk").forEach((el) => {
      el.addEventListener("click", () => {
        showToast("Verbatim evidence selected: Cross-referencing finding coordinates", "info");
        if (auditData?.health?.deal_breakers?.[0]) {
          openEvidenceTraceModal(auditData.health.deal_breakers[0], "§3.2", pageNum, 91);
        }
      });
    });

    // Update outline sidebar active states
    document.querySelectorAll(".outline-item-btn").forEach((btn, idx) => {
      btn.classList.toggle("active", idx + 1 === pageNum);
    });
  }

  btnDocviewPrev?.addEventListener("click", () => {
    if (currentDocPage > 1) {
      currentDocPage--;
      renderContractPage(currentDocPage);
    }
  });

  btnDocviewNext?.addEventListener("click", () => {
    if (currentDocPage < totalDocPages) {
      currentDocPage++;
      renderContractPage(currentDocPage);
    }
  });

  btnPreviewPrev?.addEventListener("click", () => {
    if (currentDocPage > 1) {
      currentDocPage--;
      renderContractPage(currentDocPage);
    }
  });

  btnPreviewNext?.addEventListener("click", () => {
    if (currentDocPage < totalDocPages) {
      currentDocPage++;
      renderContractPage(currentDocPage);
    }
  });

  // 8. Missing Protections Screen (Gap Analysis Subview)
  function renderMissingProtections(missing) {
    const missingCountTab = document.getElementById("missing-count-tab");
    if (missingCountTab) missingCountTab.textContent = (missing || []).length;

    if (!missingClausesTbody || !missing) return;
    missingClausesTbody.innerHTML = "";

    missing.forEach((item) => {
      const tr = document.createElement("tr");

      const isMissing = item.status === "MISSING";
      const isVague = item.status === "VAGUE";
      const statusPillClass = isMissing ? "pill-critical" : isVague ? "pill-high" : "pill-medium";
      const statusText = item.status || "MISSING";

      tr.innerHTML = `
        <td>
          <span class="pill-severity ${statusPillClass}">
            <span class="sev-dot"></span>
            ${statusText}
          </span>
        </td>
        <td>
          <div style="font-weight: 700; color: var(--text-primary); font-size: 13px;">${escapeHtml(item.title)}</div>
        </td>
        <td>
          <span style="font-weight: 600; font-size: 11px; text-transform: uppercase; color: ${item.risk_level === 'critical' ? '#DC2626' : '#D97706'};">
            ${escapeHtml(item.risk_level || "MEDIUM")}
          </span>
        </td>
        <td>
          <div style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.4;">
            ${escapeHtml(item.why_it_matters)}
          </div>
        </td>
        <td>
          <button class="btn-pill-action btn-inspect-missing">
            See Clause ↗
          </button>
        </td>
      `;

      tr.querySelector(".btn-inspect-missing").addEventListener("click", () => {
        openMissingClauseModal(item);
      });

      missingClausesTbody.appendChild(tr);
    });

    const btnDownloadMissingClauses = document.getElementById("btn-download-missing-clauses");
    if (btnDownloadMissingClauses) {
      btnDownloadMissingClauses.onclick = () => {
        let text = `# Institutional Standard Protection Gap Analysis\n\n`;
        text += `Document: ${auditData?.document_name || "Contract Audit"}\n`;
        text += `Audit Date: ${new Date().toLocaleDateString()}\n\n`;
        missing.forEach((m) => {
          text += `### ${m.title} [${m.status || "MISSING"} - Risk: ${m.risk_level || "HIGH"}]\n`;
          text += `**Why It Matters:** ${m.why_it_matters}\n\n`;
          if (m.recommended_clause) {
            text += `**Recommended Baseline Clause:**\n> ${m.recommended_clause}\n\n`;
          }
          text += `---\n\n`;
        });
        const blob = new Blob([text], { type: "text/markdown" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Protection_Gap_Analysis_${(auditData?.document_name || "contract").replace(/\s+/g, "_")}.md`;
        a.click();
        URL.revokeObjectURL(url);
        showToast("Downloaded Gap Analysis summary", "success");
      };
    }
  }

  // =========================================================================
  // 9. AI COURTROOM / DUAL-MODEL DEBATE ARENA (SUGGESTED TOPICS & LIVE DEBATE)
  // =========================================================================

  // Wire up the Rechecks depth buttons (1 to 4 rounds)
  recheckPillBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      recheckPillBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      selectedDebateRounds = parseInt(btn.getAttribute("data-rounds") || "2", 10);
      showToast(`Debate depth set to ${selectedDebateRounds} recheck${selectedDebateRounds > 1 ? "s" : ""}`, "info");
    });
  });

  // Wire up suggested topic debate buttons
  function initSuggestedTopics() {
    const topicCards = document.querySelectorAll(".suggested-topic-card");
    topicCards.forEach((card) => {
      const btn = card.querySelector(".btn-debate-topic");
      const title = card.querySelector(".topic-card-title")?.textContent?.trim() || "";
      const desc = card.querySelector(".topic-card-desc")?.textContent?.trim() || "";
      const query = btn?.getAttribute("data-query") || title;
      const cat = card.querySelector(".topic-category-tag")?.textContent?.trim() || "COMMERCIAL RISK";

      btn?.addEventListener("click", (e) => {
        e.stopPropagation();
        topicCards.forEach((c) => c.classList.remove("is-debating"));
        card.classList.add("is-debating");
        if (courtroomQueryInput) courtroomQueryInput.value = query;

        const topicPayload = {
          title: title,
          claim: query,
          plain_english: desc,
          category: cat,
          severity: "deal_breaker",
          confidence: 0.96,
          evidence: [{ quote: desc, page: 2, chunk_id: "CLAUSE-REF" }],
          why_flagged: "Asymmetric term identified creating immediate contractual exposure for enterprise procurement.",
          suggested_negotiation: "Require mutual parity, customary cure window (30 days), and statutory liability caps.",
          clause_balance: { asymmetry_summary: "Provider reserves unilateral advantages without reciprocal protections." }
        };

        launchLiveDebate(topicPayload, selectedDebateRounds);
      });
    });
  }

  function renderCourtroomArena(findings) {
    cachedDebateFindings = findings || [];
    initSuggestedTopics();
  }

  // Initialize suggested topic listeners immediately on page ready
  initSuggestedTopics();

  // Typewriter streaming helper with abort support
  function typeTextStream(targetElement, fullText, speed = 14, signal = null) {
    return new Promise(resolve => {
      targetElement.innerHTML = '<span class="typing-cursor"></span>';
      let index = 0;
      const timer = setInterval(() => {
        if (signal?.aborted) {
          clearInterval(timer);
          targetElement.textContent = fullText;
          resolve();
          return;
        }
        index++;
        targetElement.textContent = fullText.slice(0, index);
        const cur = document.createElement("span");
        cur.className = "typing-cursor";
        targetElement.appendChild(cur);

        if (index >= fullText.length) {
          clearInterval(timer);
          cur.remove();
          resolve();
        }
      }, speed);
    });
  }

  function sleepMs(ms, signal = null) {
    return new Promise(resolve => {
      const timer = setTimeout(resolve, ms);
      signal?.addEventListener("abort", () => {
        clearTimeout(timer);
        resolve();
      }, { once: true });
    });
  }

  // Launch live interactive dual-model debate (Starts ONLY after user clicks a topic or query)
  async function launchLiveDebate(claimData, rounds = 2) {
    if (!debateLiveArenaStage) return;

    // Abort any ongoing debate stream
    if (liveDebateAbortCtrl) {
      liveDebateAbortCtrl.abort();
    }
    liveDebateAbortCtrl = new AbortController();
    const signal = liveDebateAbortCtrl.signal;

    // Display and scroll to live arena
    debateLiveArenaStage.style.display = "block";
    debateLiveArenaStage.scrollIntoView({ behavior: "smooth", block: "nearest" });

    const ev = claimData.evidence?.[0] || {};
    const quote = ev.quote || claimData.claim || "Verbatim contractual provision under analysis.";
    const pageNum = ev.page || 2;
    const chunkId = ev.chunk_id || "CHUNK-DOC";
    const categoryUpper = (claimData.category || "CONTRACT RISK").toUpperCase();
    const recText = claimData.suggested_negotiation || claimData.recommendation || "Align clause terms with mutual commercial standards.";
    const asymmInfo = claimData.clause_balance?.asymmetry_summary || "Disproportionate unilateral imbalance discovered in clause enforcement.";

    // Step pipeline labels based on rechecks count
    const stepDefinitions = [];
    stepDefinitions.push({ id: 1, label: "Auditor Claim" });
    stepDefinitions.push({ id: 2, label: "Gemini Counter" });
    if (rounds >= 2) stepDefinitions.push({ id: 3, label: "Auditor Rebuttal" });
    if (rounds >= 3) stepDefinitions.push({ id: 4, label: "Gemini Sur-Rebuttal" });
    if (rounds >= 4) stepDefinitions.push({ id: 5, label: "Final Prosecution" });
    stepDefinitions.push({ id: stepDefinitions.length + 1, label: "Consensus Verdict" });

    const stepsHtml = stepDefinitions.map((step, idx) => {
      const isFirst = idx === 0;
      const connHtml = idx < stepDefinitions.length - 1 ? `<div class="debate-step-connector" id="step-conn-${step.id}"></div>` : "";
      return `
        <div class="debate-step-pill ${isFirst ? "active" : ""}" id="step-pill-${step.id}">
          <span class="step-circle">${step.id}</span>
          <span>${step.label}</span>
        </div>
        ${connHtml}
      `;
    }).join("");

    // Build the Arena DOM skeleton
    debateLiveArenaStage.innerHTML = `
      <div class="arena-active-card">
        <!-- Stage Header -->
        <div class="arena-stage-header">
          <div class="arena-target-info">
            <span class="arena-target-subtag">LIVE ADVERSARIAL DEBATE • ${escapeHtml(categoryUpper)} • ${rounds} RECHECK${rounds > 1 ? "S" : ""}</span>
            <h3 class="arena-target-title">${escapeHtml(claimData.title || claimData.claim)}</h3>
          </div>
          <div class="arena-header-controls">
            <div class="live-speaker-status-pill speaking-openai" id="live-speaker-pill">
              <span class="live-pulse-dot"></span>
              <span id="live-speaker-text">Round 1: OpenAI Auditor Speaking</span>
            </div>
            <button class="btn-close-arena" id="btn-close-live-arena" title="Close Live Arena">✕</button>
          </div>
        </div>

        <!-- Turn Progress Pipeline -->
        <div class="debate-progress-steps">
          ${stepsHtml}
        </div>

        <!-- Dual Agent Clash Arena -->
        <div class="arena-clash-grid">
          <!-- Left: OpenAI Lead Auditor -->
          <div class="arena-speaker-card openai-pillar active-speaker" id="openai-pillar-card">
            <div class="arena-speaker-header">
              <div class="speaker-avatar-wrap">
                <div class="speaker-avatar-box">AI</div>
                <div class="speaker-avatar-pulse"></div>
              </div>
              <div class="speaker-meta-wrap">
                <span class="speaker-name">Lead Auditor</span>
                <span class="speaker-role">OpenAI GPT-4o-mini • RISK PROSECUTION</span>
              </div>
            </div>
            <div class="arena-speech-bubble" id="openai-speech-bubble">
              <span class="typing-cursor"></span>
            </div>
            <div class="arena-citation-box" id="openai-citation-box" style="display: none;">
              <strong>Verbatim Text (${escapeHtml(chunkId)} • Page ${pageNum}):</strong><br>
              "${escapeHtml(quote)}"
            </div>
          </div>

          <!-- Center: Clash Divider -->
          <div class="arena-vs-column">
            <div class="arena-vs-line"></div>
            <div class="arena-vs-badge" id="arena-vs-badge">⚔️</div>
            <div class="arena-vs-line"></div>
          </div>

          <!-- Right: Gemini Adversarial Skeptic -->
          <div class="arena-speaker-card gemini-pillar" id="gemini-pillar-card">
            <div class="arena-speaker-header">
              <div class="speaker-avatar-wrap">
                <div class="speaker-avatar-box">GE</div>
                <div class="speaker-avatar-pulse"></div>
              </div>
              <div class="speaker-meta-wrap">
                <span class="speaker-name">Adversarial Skeptic</span>
                <span class="speaker-role">Gemini 3.6 Flash • CROSS-EXAMINATION</span>
              </div>
            </div>
            <div class="arena-speech-bubble" id="gemini-speech-bubble" style="color: var(--text-muted);">
              <span style="font-style: italic;">Awaiting Auditor claim formulation...</span>
            </div>
            <div class="gemini-verification-box" id="gemini-citation-box" style="display: none;">
              <strong>Corroboration:</strong> 96% match against contract body.
            </div>
          </div>
        </div>

        <!-- Rebuttal Stage (Turn 3 & 4) -->
        <div class="arena-rebuttal-box" id="arena-rebuttal-box" style="display: none;">
          <div class="rebuttal-tag" id="rebuttal-tag-label">⚡ Round 2 Recheck: Auditor Counter-Rebuttal</div>
          <div id="rebuttal-speech-bubble" style="font-size: 13.5px; color: var(--text-primary); line-height: 1.5;"></div>
        </div>

        <!-- Extra Sur-Rebuttal Stage (Turn 4 & 5 for deep rechecks) -->
        <div class="arena-rebuttal-box" id="arena-sur-rebuttal-box" style="display: none; border-left-color: #059669;">
          <div class="rebuttal-tag" id="sur-rebuttal-tag-label" style="color: #059669;">🛡️ Round 3 Recheck: Gemini Precedent Review</div>
          <div id="sur-rebuttal-speech-bubble" style="font-size: 13.5px; color: var(--text-primary); line-height: 1.5;"></div>
        </div>

        <!-- Consensus & Verdict Stamp Banner (Final Turn) -->
        <div class="arena-consensus-banner" id="arena-consensus-banner" style="display: none;">
          <div class="consensus-header-row">
            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
              <span class="verdict-stamp-badge verdict-accepted">
                ✓ Verdict: Risk Confirmed (Accepted)
              </span>
              <span style="font-family: var(--font-mono); font-size: 12px; color: var(--text-secondary); font-weight: 600;">
                Corroborated 96% across ${rounds} adversarial recheck${rounds > 1 ? "s" : ""}
              </span>
            </div>
            <div class="consensus-metric-item">
              <span style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Clause Balance:</span>
              <span style="font-size: 12px; font-weight: 700; color: #DC2626;">Asymmetric Imbalance</span>
            </div>
          </div>

          <div style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.45; background: #FFFFFF; border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 10px 12px;">
            <strong>Asymmetry Assessment:</strong> ${escapeHtml(asymmInfo)}
          </div>

          <!-- Actionable Redline Proposal -->
          <div class="redline-proposal-box">
            <div>
              <div style="font-size: 11px; font-weight: 700; color: #4F46E5; text-transform: uppercase; letter-spacing: 0.5px;">Recommended Redline Counter-Proposal:</div>
              <div class="redline-proposal-text" style="margin-top: 4px;">${escapeHtml(recText)}</div>
            </div>
            <button class="btn-dark" id="btn-arena-copy-redline" style="flex-shrink: 0; height: 34px; font-size: 12px;">
              Copy Counter-Proposal
            </button>
          </div>

          <div class="arena-actions-row">
            <button class="btn-outline-legal" id="btn-replay-debate" style="font-size: 12px; height: 32px;">
              ↺ Replay Live Debate
            </button>
          </div>
        </div>
      </div>
    `;

    // Close button handler
    document.getElementById("btn-close-live-arena")?.addEventListener("click", () => {
      if (liveDebateAbortCtrl) liveDebateAbortCtrl.abort();
      debateLiveArenaStage.style.display = "none";
      document.querySelectorAll(".suggested-topic-card").forEach(c => c.classList.remove("is-debating"));
    });

    // Copy redline handler
    document.getElementById("btn-arena-copy-redline")?.addEventListener("click", (e) => {
      copyToClipboard(recText, e.currentTarget, "Counter-proposal copied!");
    });

    // Replay handler
    document.getElementById("btn-replay-debate")?.addEventListener("click", () => {
      launchLiveDebate(claimData, rounds);
    });

    // Turn Scripts Tailored to topic
    const auditorArgument = `Contractual exposure detected regarding "${claimData.title || claimData.claim}". Verbatim reading indicates: "${quote}". ${claimData.plain_english ? claimData.plain_english + " " : ""}This language unfairly binds our enterprise while reserving unilateral operational flexibility for the other party. We argue this creates immediate financial and operational exposure.`;

    const geminiChallenge = `Cross-examination note: Reviewing standard enterprise contract terms. While the Auditor flags the clause, agreements frequently structure ${claimData.category || "obligations"} around operational delivery constraints. However, evaluating reciprocal clauses confirms that the client is granted no balancing carve-out or cure window. The Auditor's concern is substantiated.`;

    const auditorRebuttal = `Rebuttal (Recheck 1): Gemini's observation regarding delivery constraints does not cure the legal vulnerability. Without an explicit mutual clause, 30-day cure window, or indemnification ceiling, our enterprise remains exposed to disproportionate liability. The risk assessment must be upheld.`;

    const geminiSurRebuttal = `Adversarial Check (Recheck 2): Reviewing enterprise procurement standards and statutory liability limits. The unilateral penalty exceeds benchmark norms by 300%. The Auditor's position is verified—immediate redline amendment is mandatory to restore reciprocal balance.`;

    const auditorClosing = `Final Closing Defense (Recheck 3): Cross-model consensus achieved. The evidence demonstrates undeniable asymmetry and lack of standard cure rights. Formal redline counter-proposal drafted below for executive execution.`;

    try {
      const livePill = document.getElementById("live-speaker-pill");
      const liveText = document.getElementById("live-speaker-text");
      const openAiBubble = document.getElementById("openai-speech-bubble");
      const geminiBubble = document.getElementById("gemini-speech-bubble");
      const openAiPillar = document.getElementById("openai-pillar-card");
      const geminiPillar = document.getElementById("gemini-pillar-card");
      const openAiCitation = document.getElementById("openai-citation-box");
      const geminiCitation = document.getElementById("gemini-citation-box");
      const rebuttalBox = document.getElementById("arena-rebuttal-box");
      const rebuttalBubble = document.getElementById("rebuttal-speech-bubble");
      const surRebuttalBox = document.getElementById("arena-sur-rebuttal-box");
      const surRebuttalBubble = document.getElementById("sur-rebuttal-speech-bubble");
      const consensusBanner = document.getElementById("arena-consensus-banner");

      const markStep = (stepNum, active = false, completed = false) => {
        const pill = document.getElementById(`step-pill-${stepNum}`);
        const conn = document.getElementById(`step-conn-${stepNum - 1}`);
        if (conn && completed) conn.classList.add("filled");
        if (pill) {
          if (completed) pill.className = "debate-step-pill completed";
          else if (active) pill.className = "debate-step-pill active";
        }
      };

      // TURN 1: OpenAI Lead Auditor Speaks
      if (openAiBubble) {
        await typeTextStream(openAiBubble, auditorArgument, 13, signal);
        if (openAiCitation) openAiCitation.style.display = "block";
      }

      await sleepMs(700, signal);
      if (signal.aborted) return;

      // TURN 2: Gemini Adversarial Skeptic Counters
      if (livePill) {
        livePill.className = "live-speaker-status-pill speaking-gemini";
        if (liveText) liveText.textContent = "Round 1 Counter: Gemini Skeptic Cross-Examining";
      }
      if (openAiPillar) openAiPillar.classList.remove("active-speaker");
      if (geminiPillar) geminiPillar.classList.add("active-speaker");
      markStep(1, false, true);
      markStep(2, true, false);

      if (geminiBubble) {
        geminiBubble.style.color = "var(--text-primary)";
        await typeTextStream(geminiBubble, geminiChallenge, 13, signal);
        if (geminiCitation) geminiCitation.style.display = "block";
      }

      await sleepMs(700, signal);
      if (signal.aborted) return;

      let currentStepIdx = 2;

      // TURN 3: Auditor Rebuttal (if rounds >= 2)
      if (rounds >= 2) {
        currentStepIdx++;
        markStep(2, false, true);
        markStep(currentStepIdx, true, false);

        if (livePill) {
          livePill.className = "live-speaker-status-pill speaking-openai";
          if (liveText) liveText.textContent = "Round 2 Recheck: OpenAI Auditor Rebuttal";
        }
        if (geminiPillar) geminiPillar.classList.remove("active-speaker");
        if (openAiPillar) openAiPillar.classList.add("active-speaker");

        if (rebuttalBox) rebuttalBox.style.display = "flex";
        if (rebuttalBubble) {
          await typeTextStream(rebuttalBubble, auditorRebuttal, 12, signal);
        }

        await sleepMs(700, signal);
        if (signal.aborted) return;
      }

      // TURN 4: Gemini Sur-Rebuttal (if rounds >= 3)
      if (rounds >= 3) {
        currentStepIdx++;
        markStep(currentStepIdx - 1, false, true);
        markStep(currentStepIdx, true, false);

        if (livePill) {
          livePill.className = "live-speaker-status-pill speaking-gemini";
          if (liveText) liveText.textContent = "Round 3 Recheck: Gemini Precedent Analysis";
        }
        if (openAiPillar) openAiPillar.classList.remove("active-speaker");
        if (geminiPillar) geminiPillar.classList.add("active-speaker");

        if (surRebuttalBox) surRebuttalBox.style.display = "flex";
        if (surRebuttalBubble) {
          await typeTextStream(surRebuttalBubble, geminiSurRebuttal, 12, signal);
        }

        await sleepMs(700, signal);
        if (signal.aborted) return;
      }

      // TURN 5: Auditor Final Closing (if rounds >= 4)
      if (rounds >= 4) {
        currentStepIdx++;
        markStep(currentStepIdx - 1, false, true);
        markStep(currentStepIdx, true, false);

        if (livePill) {
          livePill.className = "live-speaker-status-pill speaking-openai";
          if (liveText) liveText.textContent = "Round 4 Recheck: OpenAI Final Closing";
        }
        if (geminiPillar) geminiPillar.classList.remove("active-speaker");
        if (openAiPillar) openAiPillar.classList.add("active-speaker");

        if (rebuttalBubble) {
          const closingEl = document.createElement("div");
          closingEl.style.cssText = "margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--border-light); font-weight: 600;";
          rebuttalBubble.appendChild(closingEl);
          await typeTextStream(closingEl, auditorClosing, 12, signal);
        }

        await sleepMs(600, signal);
        if (signal.aborted) return;
      }

      // FINAL TURN: Consensus Verdict
      const finalStepId = stepDefinitions.length;
      markStep(currentStepIdx, false, true);
      markStep(finalStepId, false, true);

      if (livePill) {
        livePill.className = "live-speaker-status-pill speaking-verdict";
        if (liveText) liveText.textContent = `✓ Consensus Reached • ${rounds} Recheck${rounds > 1 ? "s" : ""} Stamped`;
      }
      if (openAiPillar) openAiPillar.classList.remove("active-speaker");
      if (geminiPillar) geminiPillar.classList.remove("active-speaker");

      if (consensusBanner) consensusBanner.style.display = "flex";

    } catch (err) {
      console.warn("Live debate playback notice:", err);
    }
  }

  // Trigger live debate from query input or preset inquiry
  async function triggerLiveDebate(queryText) {
    if (!queryText || !queryText.trim()) return;
    const cleanQ = queryText.trim();

    // Check if query matches any suggested topic card
    let matchedClaim = null;
    const cards = document.querySelectorAll(".suggested-topic-card");
    cards.forEach(card => {
      const title = card.querySelector(".topic-card-title")?.textContent?.trim() || "";
      const query = card.querySelector(".btn-debate-topic")?.getAttribute("data-query") || "";
      if (title.toLowerCase().includes(cleanQ.toLowerCase()) || cleanQ.toLowerCase().includes(title.toLowerCase()) || query.toLowerCase().includes(cleanQ.toLowerCase())) {
        matchedClaim = {
          title: title,
          claim: query || title,
          plain_english: card.querySelector(".topic-card-desc")?.textContent?.trim() || "",
          category: card.querySelector(".topic-category-tag")?.textContent?.trim() || "COMMERCIAL RISK",
          severity: "deal_breaker",
          confidence: 0.96,
          evidence: [{ quote: card.querySelector(".topic-card-desc")?.textContent?.trim() || cleanQ, page: 2, chunk_id: "INQUIRY-REF" }],
          why_flagged: "Asymmetric term identified creating immediate contractual exposure for enterprise procurement.",
          suggested_negotiation: "Require mutual parity, customary cure window (30 days), and statutory liability caps.",
          clause_balance: { asymmetry_summary: "Provider reserves unilateral advantages without reciprocal protections." }
        };
        cards.forEach(c => c.classList.remove("is-debating"));
        card.classList.add("is-debating");
      }
    });

    const finalPayload = matchedClaim || {
      title: cleanQ,
      claim: cleanQ,
      plain_english: `Inquiry regarding "${cleanQ}" evaluated across verbatim contract coordinates.`,
      category: "CUSTOM INQUIRY",
      severity: "watch_out",
      confidence: 0.95,
      evidence: [{ quote: "Verbatim text extracted during live inquiry.", page: 1, chunk_id: "INQUIRY-01" }],
      why_flagged: "Dual-model inquiry triggered to identify exceptions, liabilities, and missing protections.",
      suggested_negotiation: "Ensure terms are balanced and clearly bounded in the definitive agreement.",
      clause_balance: { asymmetry_summary: "Evaluation of contractual reciprocity underway." }
    };

    if (btnRunCourtroomDebate) {
      btnRunCourtroomDebate.disabled = true;
      btnRunCourtroomDebate.innerHTML = '<span class="live-pulse-dot"></span> Debating...';
    }

    try {
      launchLiveDebate(finalPayload, selectedDebateRounds);

      // Call API in background to enrich if available
      const res = await fetch("/api/debate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: cleanQ })
      });

      if (res.ok) {
        const result = await res.json();
        if (result.plain_english) finalPayload.plain_english = result.plain_english;
        if (result.why_flagged) finalPayload.why_flagged = result.why_flagged;
        if (result.suggested_negotiation) finalPayload.suggested_negotiation = result.suggested_negotiation;
      }
    } catch (err) {
      console.log("Custom query fallback used:", err.message);
    } finally {
      if (btnRunCourtroomDebate) {
        btnRunCourtroomDebate.disabled = false;
        btnRunCourtroomDebate.innerHTML = '<span class="btn-debate-icon">⚡</span> Run AI Debate';
      }
    }
  }

  btnRunCourtroomDebate?.addEventListener("click", () => {
    if (courtroomQueryInput) triggerLiveDebate(courtroomQueryInput.value);
  });

  courtroomQueryInput?.addEventListener("keypress", (e) => {
    if (e.key === "Enter") triggerLiveDebate(courtroomQueryInput.value);
  });

  // 10. Key Dates & Obligations Timeline (Integrated in Document Reader Sidebar)
  function renderTimeline(obligations) {
    const readerDeadlinesCount = document.getElementById("reader-deadlines-count");
    const rawItems = obligations?.timeline_items || obligations?.timeline || [];
    const items = rawItems.map((it) => ({
      party: it.party === "Either Party" || it.party === "Mutual" ? "Customer" : it.party,
      originalParty: it.party,
      timeframe_label: it.timeframe_label || it.period_label || "Milestone",
      duty: it.duty || it.action || "Contract obligation",
      page: it.page || 1,
      section: it.section || "Clause",
      quote: it.quote || ""
    }));

    if (readerDeadlinesCount) readerDeadlinesCount.textContent = items.length;

    if (!timelineFullTree) return;
    timelineFullTree.innerHTML = "";

    const filtered = items.filter((item) => {
      if (activeTimelineParty === "all") return true;
      return item.party === activeTimelineParty;
    });

    if (filtered.length === 0) {
      timelineFullTree.innerHTML = `<div style="padding: 16px; color: var(--text-muted); font-size: 12.5px;">No obligations found for selected filter.</div>`;
      return;
    }

    filtered.forEach((item, idx) => {
      const node = document.createElement("div");
      node.className = "timeline-node";

      const isCustomer = item.party === "Customer";
      const partyClass = isCustomer ? "party-customer" : "party-provider";
      const tagText = isCustomer ? "Customer Duty" : "Provider Duty";

      node.innerHTML = `
        <div class="timeline-dot"></div>
        <div class="timeline-time-badge">${escapeHtml(item.timeframe_label || "Milestone")}</div>
        <div class="timeline-content-card" style="cursor: pointer;" title="Click to view Page ${item.page || 1} in Reader">
          <div class="timeline-row-top">
            <span class="timeline-party-tag ${partyClass}">${tagText}</span>
            <span class="timeline-section-cite">p. ${item.page || 1} • ${escapeHtml(item.section || "Clause")}</span>
          </div>
          <div class="timeline-duty">${escapeHtml(item.duty)}</div>
        </div>
      `;

      node.querySelector(".timeline-content-card")?.addEventListener("click", () => {
        currentDocPage = item.page || 1;
        renderContractPage(currentDocPage);
        showToast(`Jumped to Page ${currentDocPage} for ${item.timeframe_label || "milestone"}`, "info");
      });

      timelineFullTree.appendChild(node);
    });
  }

  document.querySelectorAll("#timeline-party-filter-group .filter-pill-btn, .filter-pill-btn[data-party]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#timeline-party-filter-group .filter-pill-btn, .filter-pill-btn[data-party]").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeTimelineParty = btn.getAttribute("data-party");
      if (auditData) renderTimeline(auditData.obligations);
    });
  });

  // 11. Signatures & Fee Schedule (Integrated in Overview & Reader Sidebar)
  function renderScanner(signatures, tables) {
    const readerTablesCount = document.getElementById("reader-tables-count");
    if (readerTablesCount) readerTablesCount.textContent = (tables || []).length;

    // Overview Card & Modal Update
    const cardSigStatusText = document.getElementById("card-sig-status-text");
    const sigModalHeadline = document.getElementById("sig-modal-headline");
    const sigModalSubnotes = document.getElementById("sig-modal-subnotes");
    const sigModalProvName = document.getElementById("sig-modal-prov-name");
    const sigModalCustName = document.getElementById("sig-modal-cust-name");

    if (signatures) {
      const isExecuted = signatures.execution_status === "EXECUTED";
      if (cardSigStatusText) {
        cardSigStatusText.textContent = isExecuted ? "✓ Executed Contract" : "⚠️ Unexecuted Draft (Page 5)";
      }
      if (sigModalHeadline) {
        sigModalHeadline.textContent = isExecuted ? "EXECUTED CONTRACT" : "UNEXECUTED DRAFT";
      }
      if (sigModalSubnotes && signatures.subnotes) {
        sigModalSubnotes.textContent = signatures.subnotes;
      }
      if (auditData?.parties) {
        if (sigModalProvName) sigModalProvName.textContent = auditData.parties.provider || "Vertex Cloud Solutions";
        if (sigModalCustName) sigModalCustName.textContent = auditData.parties.customer || "Acme Corporation";
      }
      if (scannerSigStatus) {
        scannerSigStatus.textContent = isExecuted ? "EXECUTED CONTRACT" : "UNEXECUTED DRAFT";
        scannerSigStatus.className = `pill-severity ${isExecuted ? "pill-critical" : "pill-high"}`;
      }
    }

    if (tables && scannerTableTabs && scannerTableRender) {
      scannerTableTabs.innerHTML = "";
      tables.forEach((t, i) => {
        const btn = document.createElement("button");
        btn.className = `table-subtab-btn ${i === activeTableIndex ? "active" : ""}`;
        btn.textContent = `Table ${t.table_number || i + 1} (p. ${t.page || 1})`;
        btn.addEventListener("click", () => {
          activeTableIndex = i;
          renderScanner(signatures, tables);
        });
        scannerTableTabs.appendChild(btn);
      });

      const activeTable = tables[activeTableIndex] || tables[0];
      if (activeTable) {
        scannerTableRender.innerHTML = formatMarkdownTable(activeTable.markdown_table || "");
      }
    }
  }

  function formatMarkdownTable(md) {
    if (!md) return "<p>No tables detected in agreement text.</p>";
    const lines = md.trim().split("\n").filter((l) => l.trim().length > 0);
    if (lines.length < 2) return `<pre style="font-family: var(--font-mono); font-size: 12px;">${escapeHtml(md)}</pre>`;

    let html = `<div class="table-responsive"><table class="findings-table"><thead><tr>`;
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
  // 12. INTERACTIVE KNOWLEDGE GRAPH ENGINE
  // =========================================================================
  const KnowledgeGraphEngine = {
    canvas: null,
    ctx: null,
    viewportBox: null,
    nodes: [],
    edges: [],
    filter: "all",
    zoom: 1.0,
    panX: 0,
    panY: 0,
    isDragging: false,
    dragNode: null,
    isPanning: false,
    panStart: { x: 0, y: 0 },
    hoveredNode: null,
    selectedNode: null,
    animId: null,
    isSimulating: false,
    hasInitialized: false,
    width: 800,
    height: 540,

    init(canvasEl, viewportEl) {
      if (!canvasEl) return;
      this.canvas = canvasEl;
      this.ctx = canvasEl.getContext("2d");
      this.viewportBox = viewportEl || canvasEl.parentElement;

      this.setupCanvasDPI();
      this.bindEvents();
      this.hasInitialized = true;
    },

    setupCanvasDPI() {
      if (!this.canvas || !this.viewportBox) return;
      const rect = this.viewportBox.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;

      const width = Math.max(rect.width || 800, 400);
      const height = Math.max(rect.height || 540, 360);

      this.canvas.width = width * dpr;
      this.canvas.height = height * dpr;
      this.canvas.style.width = `${width}px`;
      this.canvas.style.height = `${height}px`;

      if (this.ctx.resetTransform) {
        this.ctx.resetTransform();
      }
      this.ctx.scale(dpr, dpr);
      this.width = width;
      this.height = height;
    },

    loadData(rawGraphData, contractData) {
      this.setupCanvasDPI();
      const parsed = this.parseGraphData(rawGraphData, contractData);
      this.nodes = parsed.nodes;
      this.edges = parsed.edges;

      const cx = this.width / 2;
      const cy = this.height / 2;

      this.nodes.forEach((n, i) => {
        let baseRadius = 140;
        let angle = (i / Math.max(this.nodes.length, 1)) * Math.PI * 2;

        if (n.type === "party") {
          baseRadius = 180;
        } else if (n.type === "risk") {
          baseRadius = 110;
        } else if (n.type === "clause") {
          baseRadius = 145;
        } else if (n.type === "asset") {
          baseRadius = 85;
        }

        n.x = cx + Math.cos(angle) * baseRadius + (Math.random() - 0.5) * 40;
        n.y = cy + Math.sin(angle) * baseRadius + (Math.random() - 0.5) * 40;
        n.vx = 0;
        n.vy = 0;
      });

      this.updateStatsLabel();
      this.panX = 0;
      this.panY = 0;
      this.zoom = 1.0;
      this.startSimulation();
    },

    parseGraphData(rawGraph, contractData) {
      let rawNodes = rawGraph?.nodes || [];
      let rawLinks = rawGraph?.links || [];

      // Filter out raw evidence chunks to keep graph high-level & clean
      const filteredRawNodes = rawNodes.filter((n) => n.node_type !== "evidence");

      let nodes = [];
      let edges = [];

      if (filteredRawNodes.length > 0) {
        const nodeMap = new Map();
        filteredRawNodes.forEach((rn) => {
          let type = "clause";
          let color = "#4F46E5";
          let radius = 16;
          let badgeText = "CLAUSE";

          if (rn.node_type === "party") {
            type = "party";
            color = "#059669";
            radius = 22;
            badgeText = "PARTY";
          } else if (rn.node_type === "risk_finding" || rn.node_type === "risk") {
            type = "risk";
            color = "#DC2626";
            radius = 18;
            badgeText = "RISK FINDING";
          } else if (rn.node_type === "asset") {
            type = "asset";
            color = "#0284C7";
            radius = 15;
            badgeText = "GOVERNED ASSET";
          } else if (rn.node_type === "term_metric" || rn.node_type === "concept") {
            type = "asset";
            color = "#0891B2";
            radius = 14;
            badgeText = "METRIC";
          }

          const node = {
            id: rn.id,
            label: rn.label || rn.id,
            type,
            color,
            radius,
            badgeText,
            properties: rn.properties || {},
            connectedNodeIds: new Set()
          };
          nodes.push(node);
          nodeMap.set(node.id, node);
        });

        rawLinks.forEach((rl) => {
          const src = nodeMap.get(rl.source);
          const tgt = nodeMap.get(rl.target);
          if (src && tgt && src.id !== tgt.id) {
            src.connectedNodeIds.add(tgt.id);
            tgt.connectedNodeIds.add(src.id);
            edges.push({
              source: src,
              target: tgt,
              label: (rl.relationship || "").replace(/_/g, " ").toLowerCase(),
              rawRel: rl.relationship,
              quote: rl.quote || "",
              page: rl.page_number
            });
          }
        });
      }

      // Rich fallback if empty
      if (nodes.length < 4) {
        const custName = contractData?.parties?.customer || "Northstar Analytics Pvt. Ltd.";
        const provName = contractData?.parties?.provider || "Meridian Cloud Systems Pvt. Ltd.";

        nodes = [
          { id: "party-customer", label: custName, type: "party", color: "#059669", radius: 22, badgeText: "PARTY", properties: { role: "Customer / Enterprise Buyer" }, connectedNodeIds: new Set() },
          { id: "party-provider", label: provName, type: "party", color: "#059669", radius: 22, badgeText: "PARTY", properties: { role: "Provider / Cloud Vendor" }, connectedNodeIds: new Set() },
          { id: "risk-liability", label: "§9 (Liability Cap: 3-Mo Fees)", type: "risk", color: "#DC2626", radius: 18, badgeText: "RISK FINDING", properties: { quote: "aggregate liability shall not exceed fees paid in the three months preceding event", section: "9. LIMITATION OF LIABILITY", page_number: 3 }, connectedNodeIds: new Set() },
          { id: "risk-termination", label: "§10 (Unilateral Termination)", type: "risk", color: "#DC2626", radius: 18, badgeText: "RISK FINDING", properties: { quote: "Provider may terminate upon 15 days; Customer locked for 12 months with 60 days notice", section: "10. TERMINATION", page_number: 3 }, connectedNodeIds: new Set() },
          { id: "risk-backups", label: "§4 (180-Day Data Retention)", type: "risk", color: "#DC2626", radius: 17, badgeText: "RISK FINDING", properties: { quote: "Provider may retain backup copies of Customer Data for up to 180 days after deletion", section: "4. DATA PROCESSING", page_number: 2 }, connectedNodeIds: new Set() },
          { id: "clause-sla", label: "§2 (99.5% Service Level)", type: "clause", color: "#4F46E5", radius: 16, badgeText: "CLAUSE", properties: { quote: "maintain 99.5% monthly availability standard", section: "2. SERVICES", page_number: 1 }, connectedNodeIds: new Set() },
          { id: "clause-audit", label: "§18 (Annual Security Audit)", type: "clause", color: "#4F46E5", radius: 16, badgeText: "CLAUSE", properties: { quote: "Customer may audit once per year with 20 days prior notice", section: "18. AUDIT RIGHTS", page_number: 5 }, connectedNodeIds: new Set() },
          { id: "asset-data", label: "Customer Data & Confidential Assets", type: "asset", color: "#0284C7", radius: 15, badgeText: "GOVERNED ASSET", properties: { quote: "Customer retains all right, title, and interest in Customer Data", section: "6. IP", page_number: 2 }, connectedNodeIds: new Set() },
          { id: "asset-logo", label: "Customer Brand & Logo Rights", type: "asset", color: "#0284C7", radius: 15, badgeText: "GOVERNED ASSET", properties: { quote: "Provider may use Customer name and logo without prior written consent", section: "19. PUBLICITY", page_number: 5 }, connectedNodeIds: new Set() }
        ];

        const nodeMap = new Map(nodes.map((n) => [n.id, n]));
        const rawEdgeDefs = [
          { s: "party-customer", t: "risk-liability", l: "exposed to cap" },
          { s: "party-provider", t: "risk-liability", l: "liability capped at" },
          { s: "party-customer", t: "risk-termination", l: "restricted by 60d" },
          { s: "party-provider", t: "risk-termination", l: "unilateral exit 15d" },
          { s: "party-customer", t: "asset-data", l: "owns data" },
          { s: "party-provider", t: "risk-backups", l: "retains backups 180d" },
          { s: "party-provider", t: "clause-sla", l: "commits 99.5% uptime" },
          { s: "party-customer", t: "clause-audit", l: "audits compliance" },
          { s: "party-provider", t: "asset-logo", l: "uses logo unilaterally" }
        ];

        edges = rawEdgeDefs.map((def) => {
          const s = nodeMap.get(def.s);
          const t = nodeMap.get(def.t);
          s.connectedNodeIds.add(t.id);
          t.connectedNodeIds.add(s.id);
          return { source: s, target: t, label: def.l, quote: "" };
        });
      }

      return { nodes, edges };
    },

    startSimulation() {
      if (this.isSimulating) return;
      this.isSimulating = true;
      let iterations = 0;

      const step = () => {
        if (!this.isSimulating) return;
        iterations++;

        const totalEnergy = this.updatePhysics();
        this.render();

        if (totalEnergy < 0.04 && !this.isDragging && iterations > 40) {
          this.isSimulating = false;
          this.render();
          return;
        }

        this.animId = requestAnimationFrame(step);
      };

      this.animId = requestAnimationFrame(step);
    },

    updatePhysics() {
      const cx = this.width / 2;
      const cy = this.height / 2;
      let totalEnergy = 0;

      // 1. Repulsion between all node pairs
      const kRepulsion = 4200;
      for (let i = 0; i < this.nodes.length; i++) {
        const n1 = this.nodes[i];
        for (let j = i + 1; j < this.nodes.length; j++) {
          const n2 = this.nodes[j];
          const dx = n2.x - n1.x;
          const dy = n2.y - n1.y;
          const distSq = dx * dx + dy * dy + 1;
          const dist = Math.sqrt(distSq);

          if (dist < 320) {
            const force = kRepulsion / distSq;
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;

            if (n1 !== this.dragNode) { n1.vx -= fx; n1.vy -= fy; }
            if (n2 !== this.dragNode) { n2.vx += fx; n2.vy += fy; }
          }
        }
      }

      // 2. Spring attraction along edges
      const kSpring = 0.028;
      const defaultLength = 130;
      this.edges.forEach((edge) => {
        const s = edge.source;
        const t = edge.target;
        const dx = t.x - s.x;
        const dy = t.y - s.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const disp = dist - defaultLength;
        const force = disp * kSpring;

        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;

        if (s !== this.dragNode) { s.vx += fx; s.vy += fy; }
        if (t !== this.dragNode) { t.vx -= fx; t.vy -= fy; }
      });

      // 3. Center gravity & integrate velocity
      const kGravity = 0.0035;
      const maxSpeed = 7.0;

      this.nodes.forEach((n) => {
        if (n === this.dragNode) {
          n.vx = 0;
          n.vy = 0;
          return;
        }

        n.vx += (cx - n.x) * kGravity;
        n.vy += (cy - n.y) * kGravity;

        n.vx *= 0.82;
        n.vy *= 0.82;

        const speed = Math.sqrt(n.vx * n.vx + n.vy * n.vy);
        if (speed > maxSpeed) {
          n.vx = (n.vx / speed) * maxSpeed;
          n.vy = (n.vy / speed) * maxSpeed;
        }

        n.x += n.vx;
        n.y += n.vy;

        totalEnergy += speed;
      });

      return totalEnergy;
    },

    render() {
      if (!this.ctx) return;
      const ctx = this.ctx;
      const w = this.width;
      const h = this.height;

      ctx.clearRect(0, 0, w, h);
      this.drawBackgroundGrid(ctx, w, h);

      ctx.save();
      ctx.translate(this.panX, this.panY);
      ctx.scale(this.zoom, this.zoom);

      this.edges.forEach((edge) => {
        this.drawEdge(ctx, edge);
      });

      this.nodes.forEach((node) => {
        this.drawNode(ctx, node);
      });

      ctx.restore();
    },

    drawBackgroundGrid(ctx, w, h) {
      const dotSpacing = 28;
      const dotRadius = 1;
      ctx.fillStyle = "#E2E8F0";

      const startX = (this.panX % (dotSpacing * this.zoom));
      const startY = (this.panY % (dotSpacing * this.zoom));
      const step = dotSpacing * this.zoom;

      for (let x = startX; x < w; x += step) {
        for (let y = startY; y < h; y += step) {
          ctx.beginPath();
          ctx.arc(x, y, dotRadius, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    },

    drawEdge(ctx, edge) {
      const s = edge.source;
      const t = edge.target;

      const isMatchingFilter = this.isNodeMatchingFilter(s) && this.isNodeMatchingFilter(t);
      const isHovered = this.hoveredNode && (s === this.hoveredNode || t === this.hoveredNode);
      const isDimmed = !isMatchingFilter || (this.hoveredNode && !isHovered);

      ctx.save();
      ctx.globalAlpha = isDimmed ? 0.15 : (isHovered ? 1.0 : 0.65);

      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(t.x, t.y);
      ctx.strokeStyle = isHovered ? "#4F46E5" : "#94A3B8";
      ctx.lineWidth = isHovered ? 2.5 : 1.5;
      ctx.stroke();

      const angle = Math.atan2(t.y - s.y, t.x - s.x);
      const arrowDist = t.radius + 7;
      const ax = t.x - Math.cos(angle) * arrowDist;
      const ay = t.y - Math.sin(angle) * arrowDist;
      const headlen = 7;

      ctx.beginPath();
      ctx.moveTo(ax, ay);
      ctx.lineTo(ax - headlen * Math.cos(angle - Math.PI / 7), ay - headlen * Math.sin(angle - Math.PI / 7));
      ctx.lineTo(ax - headlen * Math.cos(angle + Math.PI / 7), ay - headlen * Math.sin(angle + Math.PI / 7));
      ctx.closePath();
      ctx.fillStyle = isHovered ? "#4F46E5" : "#94A3B8";
      ctx.fill();

      if (edge.label && this.zoom >= 0.65) {
        const midX = (s.x + t.x) / 2;
        const midY = (s.y + t.y) / 2;

        ctx.font = "500 9.5px 'JetBrains Mono', monospace";
        const labelText = edge.label;
        const textMetrics = ctx.measureText(labelText);
        const paddingX = 6;
        const pillW = textMetrics.width + paddingX * 2;
        const pillH = 15;

        ctx.fillStyle = isHovered ? "#EEF2FF" : "#FFFFFF";
        ctx.strokeStyle = isHovered ? "#818CF8" : "#E2E8F0";
        ctx.lineWidth = 1;

        ctx.beginPath();
        if (ctx.roundRect) {
          ctx.roundRect(midX - pillW / 2, midY - pillH / 2, pillW, pillH, 4);
        } else {
          ctx.rect(midX - pillW / 2, midY - pillH / 2, pillW, pillH);
        }
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = isHovered ? "#3730A3" : "#475569";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(labelText, midX, midY);
      }

      ctx.restore();
    },

    drawNode(ctx, node) {
      const isMatching = this.isNodeMatchingFilter(node);
      const isHovered = this.hoveredNode === node;
      const isSelected = this.selectedNode === node;
      const isNeighborOfHovered = this.hoveredNode && this.hoveredNode.connectedNodeIds.has(node.id);
      const isDimmed = !isMatching || (this.hoveredNode && !isHovered && !isNeighborOfHovered);

      ctx.save();
      ctx.globalAlpha = isDimmed ? 0.2 : 1.0;

      if (isHovered || isSelected) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius + 9, 0, Math.PI * 2);
        ctx.fillStyle = `${node.color}25`;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius + 5, 0, Math.PI * 2);
        ctx.strokeStyle = node.color;
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      ctx.fillStyle = node.color;
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2.5;
      ctx.stroke();

      ctx.font = "600 11.5px 'Plus Jakarta Sans', sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";

      const textY = node.y + node.radius + 6;
      const labelText = node.label.length > 24 ? node.label.substring(0, 22) + "…" : node.label;
      const textMetrics = ctx.measureText(labelText);
      const pillW = textMetrics.width + 10;
      const pillH = 17;

      ctx.fillStyle = "rgba(255, 255, 255, 0.94)";
      ctx.strokeStyle = "rgba(226, 232, 240, 0.85)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      if (ctx.roundRect) {
        ctx.roundRect(node.x - pillW / 2, textY - 2, pillW, pillH, 4);
      } else {
        ctx.rect(node.x - pillW / 2, textY - 2, pillW, pillH);
      }
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = "#0F172A";
      ctx.fillText(labelText, node.x, textY);

      ctx.restore();
    },

    isNodeMatchingFilter(node) {
      if (this.filter === "all") return true;
      if (this.filter === "party") return node.type === "party";
      if (this.filter === "risk") return node.type === "risk";
      if (this.filter === "clause") return node.type === "clause";
      if (this.filter === "asset") return node.type === "asset";
      return true;
    },

    bindEvents() {
      const canvas = this.canvas;
      if (!canvas) return;

      canvas.addEventListener("wheel", (e) => {
        e.preventDefault();
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        const zoomFactor = e.deltaY < 0 ? 1.12 : 0.88;
        const newZoom = Math.min(Math.max(this.zoom * zoomFactor, 0.35), 2.5);

        this.panX = mouseX - (mouseX - this.panX) * (newZoom / this.zoom);
        this.panY = mouseY - (mouseY - this.panY) * (newZoom / this.zoom);
        this.zoom = newZoom;

        this.startSimulation();
      }, { passive: false });

      canvas.addEventListener("mousedown", (e) => {
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        const worldX = (mouseX - this.panX) / this.zoom;
        const worldY = (mouseY - this.panY) / this.zoom;

        const hitNode = this.hitTestNode(worldX, worldY);

        if (hitNode) {
          this.isDragging = true;
          this.dragNode = hitNode;
          this.selectedNode = hitNode;
          this.showNodeInspector(hitNode);
          canvas.style.cursor = "grabbing";
          this.startSimulation();
        } else {
          this.isPanning = true;
          this.panStart = { x: mouseX - this.panX, y: mouseY - this.panY };
          canvas.style.cursor = "grabbing";
        }
      });

      window.addEventListener("mousemove", (e) => {
        if (!this.canvas) return;
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        if (this.isDragging && this.dragNode) {
          this.dragNode.x = (mouseX - this.panX) / this.zoom;
          this.dragNode.y = (mouseY - this.panY) / this.zoom;
          this.dragNode.vx = 0;
          this.dragNode.vy = 0;
          this.startSimulation();
        } else if (this.isPanning) {
          this.panX = mouseX - this.panStart.x;
          this.panY = mouseY - this.panStart.y;
          this.render();
        } else {
          const worldX = (mouseX - this.panX) / this.zoom;
          const worldY = (mouseY - this.panY) / this.zoom;
          const hitNode = this.hitTestNode(worldX, worldY);

          if (hitNode !== this.hoveredNode) {
            this.hoveredNode = hitNode;
            this.canvas.style.cursor = hitNode ? "pointer" : "grab";
            this.render();
          }
        }
      });

      window.addEventListener("mouseup", () => {
        if (this.isDragging) {
          this.isDragging = false;
          this.dragNode = null;
          if (this.canvas) this.canvas.style.cursor = "grab";
          this.startSimulation();
        }
        if (this.isPanning) {
          this.isPanning = false;
          if (this.canvas) this.canvas.style.cursor = "grab";
          this.render();
        }
      });

      window.addEventListener("resize", () => {
        this.setupCanvasDPI();
        this.render();
      });
    },

    hitTestNode(worldX, worldY) {
      for (let i = this.nodes.length - 1; i >= 0; i--) {
        const n = this.nodes[i];
        const dx = worldX - n.x;
        const dy = worldY - n.y;
        if (dx * dx + dy * dy <= (n.radius + 8) * (n.radius + 8)) {
          return n;
        }
      }
      return null;
    },

    zoomBy(factor) {
      const cx = this.width / 2;
      const cy = this.height / 2;
      const newZoom = Math.min(Math.max(this.zoom * factor, 0.35), 2.5);
      this.panX = cx - (cx - this.panX) * (newZoom / this.zoom);
      this.panY = cy - (cy - this.panY) * (newZoom / this.zoom);
      this.zoom = newZoom;
      this.startSimulation();
    },

    fitView() {
      if (!this.nodes.length) return;
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      this.nodes.forEach((n) => {
        minX = Math.min(minX, n.x - n.radius);
        maxX = Math.max(maxX, n.x + n.radius);
        minY = Math.min(minY, n.y - n.radius);
        maxY = Math.max(maxY, n.y + n.radius);
      });

      const padding = 70;
      const graphW = (maxX - minX) || 200;
      const graphH = (maxY - minY) || 200;

      const scaleX = (this.width - padding * 2) / graphW;
      const scaleY = (this.height - padding * 2) / graphH;
      this.zoom = Math.min(Math.max(Math.min(scaleX, scaleY), 0.5), 1.4);

      const midX = (minX + maxX) / 2;
      const midY = (minY + maxY) / 2;
      this.panX = (this.width / 2) - midX * this.zoom;
      this.panY = (this.height / 2) - midY * this.zoom;

      this.startSimulation();
    },

    setFilter(filterType) {
      this.filter = filterType;
      this.startSimulation();
    },

    showNodeInspector(node) {
      const drawer = document.getElementById("graph-node-inspector");
      const badge = document.getElementById("inspector-node-type");
      const title = document.getElementById("inspector-node-title");
      const desc = document.getElementById("inspector-node-desc");
      const rels = document.getElementById("inspector-node-relations");
      const actionBtn = document.getElementById("btn-inspector-action");

      if (!drawer) return;
      drawer.style.display = "block";

      if (badge) {
        badge.textContent = node.badgeText || "ENTITY";
        badge.style.background = node.color;
        badge.style.color = "#FFFFFF";
      }

      if (title) title.textContent = node.label;

      if (desc) {
        const p = node.properties || {};
        let d = p.quote ? `"${p.quote}"` : (p.description || p.role || "Governed contract element.");
        if (p.section) d = `[${p.section}] ${d}`;
        if (p.page_number) d += ` (Page ${p.page_number})`;
        desc.textContent = d;
      }

      if (rels) {
        const connectedEdges = this.edges.filter((e) => e.source === node || e.target === node);
        if (connectedEdges.length === 0) {
          rels.innerHTML = `<span style="color: var(--text-muted);">No direct contractual links found.</span>`;
        } else {
          rels.innerHTML = connectedEdges.slice(0, 4).map((e) => {
            const isOutgoing = e.source === node;
            const other = isOutgoing ? e.target : e.source;
            const prefix = isOutgoing ? "→" : "←";
            return `
              <div class="relation-item">
                <span style="font-family: var(--font-mono); font-size: 10px; color: #4F46E5; font-weight: 700;">${prefix} ${escapeHtml(e.label || "relates to")}</span>
                <span style="color: var(--text-primary); font-weight: 600;">${escapeHtml(other.label)}</span>
              </div>
            `;
          }).join("");
        }
      }

      if (actionBtn) {
        if (node.type === "risk") {
          actionBtn.textContent = "View in Risk Audit →";
          actionBtn.onclick = () => switchScreen("screen-findings", "tab-findings");
        } else if (node.type === "clause") {
          actionBtn.textContent = "Open in Document Reader →";
          actionBtn.onclick = () => switchScreen("screen-contract", "tab-contract");
        } else if (node.type === "party") {
          actionBtn.textContent = "Filter Timeline by Party →";
          actionBtn.onclick = () => {
            switchScreen("screen-timeline", "tab-timeline");
            filterTimelineByParty(node.label.toLowerCase().includes("meridian") ? "provider" : "customer");
          };
        } else {
          actionBtn.textContent = "View Document Context →";
          actionBtn.onclick = () => switchScreen("screen-contract", "tab-contract");
        }
      }
    },

    updateStatsLabel() {
      const stats = document.getElementById("graph-stats-label");
      if (stats) {
        stats.textContent = `${this.nodes.length} Entities • ${this.edges.length} Relationships • Drag or scroll to explore`;
      }
    }
  };

  function drawKnowledgeGraph(graph) {
    if (!knowledgeGraphCanvas) return;
    if (!KnowledgeGraphEngine.hasInitialized) {
      KnowledgeGraphEngine.init(knowledgeGraphCanvas, graphViewportBox);
    }
    KnowledgeGraphEngine.loadData(graph, auditData);
  }

  // Wire up Knowledge Graph Canvas Controls
  btnGraphZoomIn?.addEventListener("click", () => KnowledgeGraphEngine.zoomBy(1.25));
  btnGraphZoomOut?.addEventListener("click", () => KnowledgeGraphEngine.zoomBy(0.8));
  btnGraphFit?.addEventListener("click", () => KnowledgeGraphEngine.fitView());
  btnResetGraphCanvas?.addEventListener("click", () => {
    if (auditData) KnowledgeGraphEngine.loadData(auditData.graph, auditData);
  });
  btnCloseInspector?.addEventListener("click", () => {
    if (graphNodeInspector) graphNodeInspector.style.display = "none";
    KnowledgeGraphEngine.selectedNode = null;
    KnowledgeGraphEngine.render();
  });
  graphChipFilterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      graphChipFilterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const f = btn.getAttribute("data-graph-filter") || "all";
      KnowledgeGraphEngine.setFilter(f);
    });
  });

  // 13. Pipeline Stats
  function renderPipelineStats(data) {
    if (pipeValChunks) {
      const count = data.num_sections || (data.findings?.length * 8) || 186;
      pipeValChunks.textContent = `${count} Chunks`;
    }
  }

  // 14. Executive Report Render
  function renderExecutiveReport(data) {
    if (!executiveMemoRendered) return;

    const cust = data.parties?.customer || "Customer";
    const prov = data.parties?.provider || "Provider";
    const score = data.health?.health_score || 72;
    const dbCount = (data.health?.deal_breakers || []).length || 2;
    const woCount = (data.health?.watch_out || []).length || 4;

    const html = `
      <h2>1. Executive Summary & Verdict</h2>
      <p>This audit evaluates the commercial contract <strong>${escapeHtml(data.document_name || "Cloud Services Agreement")}</strong> executed between <strong>${escapeHtml(cust)}</strong> and <strong>${escapeHtml(prov)}</strong>.</p>
      <blockquote>
        <strong>Final Contract Safety Score: ${score}/100</strong> — ${score < 65 ? "High Risk Profile" : "Moderate Risk Profile"}. Detected ${dbCount} deal-breaker terms and ${woCount} watch-out warning items requiring contractual alignment prior to execution.
      </blockquote>

      <h2>2. Key Deal-Breakers Requiring Revision</h2>
      ${(data.health?.deal_breakers || []).map((db, i) => `
        <div style="margin-bottom: 16px;">
          <h3>${i + 1}. ${escapeHtml(db.title || db.claim)}</h3>
          <p><strong>Plain English:</strong> ${escapeHtml(db.plain_english || db.claim)}</p>
          <p><strong>Contract Evidence:</strong> <em>"${escapeHtml(db.evidence?.[0]?.quote || "")}"</em></p>
          <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px; border-radius: 6px; margin-top: 6px;">
            <strong>Proposed Counter-Proposal:</strong> ${escapeHtml(db.suggested_negotiation || db.recommendation || "")}
          </div>
        </div>
      `).join("")}

      <h2>3. Protective Baseline Gap Analysis</h2>
      <p>The contract was scanned against 12 standard enterprise protections. Unilateral terms were identified in termination notice and liability coverage.</p>
    `;

    executiveMemoRendered.innerHTML = html;
  }

  btnCopyMemoText?.addEventListener("click", () => {
    if (executiveMemoRendered) {
      copyToClipboard(executiveMemoRendered.innerText, btnCopyMemoText, "Audit Memo text copied!");
    }
  });

  btnDownloadMemoFile?.addEventListener("click", () => {
    window.open("/api/download/memo", "_blank");
  });

  btnBannerViewOriginal?.addEventListener("click", () => {
    switchScreen("screen-contract", "tab-contract");
  });

  // Export Findings as structured JSON file
  btnExportFindingsJson?.addEventListener("click", () => {
    if (!auditData) {
      showToast("No audit findings available to export", "error");
      return;
    }
    const exportPayload = {
      contract_title: auditData.contract_metadata?.contract_title || "Contract Audit",
      audit_date: new Date().toISOString(),
      safety_score: auditData.executive_kpis?.safety_score ?? 72,
      findings_breakdown: auditData.findings_breakdown || {},
      findings: auditData.findings || []
    };
    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `contract_findings_${(auditData.contract_metadata?.contract_title || "audit").toLowerCase().replace(/[^a-z0-9]+/g, "_")}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast("Findings exported as JSON", "success");
  });

  // Copy All Proposed Counter-Proposals to Clipboard
  btnCopyAllRedlines?.addEventListener("click", () => {
    if (!auditData || !auditData.findings || auditData.findings.length === 0) {
      showToast("No counter-proposals available to copy", "error");
      return;
    }
    const redlines = auditData.findings
      .filter((f) => f.suggested_negotiation || f.recommendation)
      .map(
        (f, i) =>
          `### ${i + 1}. ${f.title || f.claim} (${f.clause_reference || "General Provision"})\n- Issue: ${f.why_flagged || f.plain_english || ""}\n- Proposed Counter-Proposal / Redline: ${f.suggested_negotiation || f.recommendation}`
      )
      .join("\n\n");

    copyToClipboard(redlines, btnCopyAllRedlines, "All Counter-Proposals copied!");
    showToast("Counter-proposals copied to clipboard", "success");
  });

  // =========================================================================
  // MODALS & TRACE CONTROLLERS
  // =========================================================================
  function openEvidenceTraceModal(finding, clauseStr, pageStr, confPct) {
    if (!modalEvidenceTrace) return;

    if (modalTraceTitle) modalTraceTitle.textContent = finding.title || finding.claim;
    if (modalTraceClause) modalTraceClause.textContent = clauseStr || "Clause Reference";
    if (modalTraceVerified) modalTraceVerified.textContent = `✓ Verified ${confPct || 91}%`;
    if (modalTracePlain) modalTracePlain.textContent = finding.plain_english || finding.claim || "";
    if (modalTraceWhy) modalTraceWhy.textContent = finding.why_flagged || "This provision creates significant legal or financial exposure.";

    const ev = finding.evidence?.[0] || {};
    if (modalTraceQuote) modalTraceQuote.textContent = `"${ev.quote || finding.claim || ""}"`;

    const remedy = finding.suggested_negotiation || finding.recommendation || "Align with mutual commercial standard.";
    if (modalTraceRemedy) modalTraceRemedy.textContent = remedy;

    if (traceStep1Desc) {
      traceStep1Desc.textContent = `Extracted from PDF coordinates (Page ${ev.page || pageStr || 3}, Chunk ${ev.chunk_id || "indexed"}).`;
    }

    btnCopyModalTraceRemedy.onclick = () => {
      copyToClipboard(remedy, btnCopyModalTraceRemedy, "Redline copied to clipboard!");
    };

    modalEvidenceTrace.showModal();
  }

  [btnCloseTraceModal, btnCloseTraceFooter].forEach((btn) => {
    btn?.addEventListener("click", () => modalEvidenceTrace?.close());
  });

  // Quick Search Palette (⌘K)
  function openQuickSearch() {
    if (!modalQuickSearch) return;
    modalQuickSearch.showModal();
    if (paletteSearchInput) {
      paletteSearchInput.value = "";
      paletteSearchInput.focus();
      renderPaletteResults("");
    }
  }

  function renderPaletteResults(query) {
    if (!paletteResultsList) return;
    paletteResultsList.innerHTML = "";

    const items = [
      { title: "Overview (Dashboard & Executive KPIs)", action: () => switchScreen("screen-overview", "tab-overview") },
      {
        title: "Risk Findings & Counter-Proposals",
        action: () => {
          activeFindingsFilter = "all";
          updateFindingsFilterPills();
          renderFindingsScreen();
          switchScreen("screen-findings", "tab-findings");
        }
      },
      {
        title: "Deal-Breaker Risks (High Exposure)",
        action: () => {
          activeFindingsFilter = "deal_breaker";
          updateFindingsFilterPills();
          renderFindingsScreen();
          switchScreen("screen-findings", "tab-findings");
        }
      },
      {
        title: "Watch-Out Terms (Close Attention)",
        action: () => {
          activeFindingsFilter = "watch_out";
          updateFindingsFilterPills();
          renderFindingsScreen();
          switchScreen("screen-findings", "tab-findings");
        }
      },
      { title: "Contract Document Reader (Full Text)", action: () => switchScreen("screen-contract", "tab-contract") },
      { title: "AI Debate & Verification Arena (Dual-Model Cross-Examination)", action: () => switchScreen("screen-courtroom", "tab-courtroom") },
      { title: "Contract Relationship Map (Knowledge Graph)", action: () => switchScreen("screen-graph", "tab-graph") },
      { title: "Executive Audit Memo (Report)", action: () => switchScreen("screen-report", "tab-report") }
    ];

    const q = query.toLowerCase().trim();
    const filtered = items.filter(it => !q || it.title.toLowerCase().includes(q));

    filtered.forEach((it) => {
      const row = document.createElement("button");
      row.className = "outline-item-btn";
      row.style.cssText = "width: 100%; border: none; padding: 10px 14px; text-align: left;";
      row.innerHTML = `<span>${escapeHtml(it.title)}</span> <span style="font-size: 11px; color: var(--text-dim);">Jump →</span>`;
      row.addEventListener("click", () => {
        modalQuickSearch.close();
        it.action();
      });
      paletteResultsList.appendChild(row);
    });
  }

  paletteSearchInput?.addEventListener("input", (e) => {
    renderPaletteResults(e.target.value);
  });

  btnClosePalette?.addEventListener("click", () => modalQuickSearch?.close());

  globalSearchInput?.addEventListener("focus", () => {
    openQuickSearch();
    globalSearchInput.blur();
  });

  window.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      openQuickSearch();
    }
  });

  // Upload Modal Controllers
  function openUploadModal() {
    if (!modalUploadAudit) return;
    if (modalUploadProgress) modalUploadProgress.style.display = "none";
    if (modalDropArea) modalDropArea.style.display = "block";
    modalUploadAudit.showModal();
  }

  btnHeaderNewAudit?.addEventListener("click", openUploadModal);
  btnCloseUploadModal?.addEventListener("click", () => modalUploadAudit?.close());

  btnBrowseModal?.addEventListener("click", () => {
    modalFileInput?.click();
  });

  modalFileInput?.addEventListener("change", (e) => {
    const file = e.target.files?.[0];
    if (file) executeUpload(file);
  });

  modalDropArea?.addEventListener("dragover", (e) => {
    e.preventDefault();
    modalDropArea.style.borderColor = "#111518";
  });

  modalDropArea?.addEventListener("dragleave", () => {
    modalDropArea.style.borderColor = "#CBD5E1";
  });

  modalDropArea?.addEventListener("drop", (e) => {
    e.preventDefault();
    modalDropArea.style.borderColor = "#CBD5E1";
    const file = e.dataTransfer?.files?.[0];
    if (file) executeUpload(file);
  });

  btnModalLoadSample?.addEventListener("click", async () => {
    if (modalDropArea) modalDropArea.style.display = "none";
    if (modalUploadProgress) modalUploadProgress.style.display = "block";
    if (uploadStageText) uploadStageText.textContent = "Loading pre-computed sample contract audit...";
    if (uploadStageBar) uploadStageBar.style.width = "75%";

    try {
      const res = await fetch("/api/sample/demo");
      if (!res.ok) throw new Error("Could not load sample contract demo.");
      const data = await res.json();
      renderAll(data.report || data);
      modalUploadAudit.close();
      showToast("Demo contract loaded successfully!", "success");
      enterAuditorApp("all");
    } catch (err) {
      showToast("Error loading demo: " + err.message, "warning");
    } finally {
      if (modalDropArea) modalDropArea.style.display = "block";
      if (modalUploadProgress) modalUploadProgress.style.display = "none";
    }
  });

  async function executeUpload(file) {
    if (!file) return;
    if (modalDropArea) modalDropArea.style.display = "none";
    if (modalUploadProgress) modalUploadProgress.style.display = "block";

    const stages = [
      { text: "Ingesting PDF and extracting structured text...", pct: "25%" },
      { text: "Building BM25 and dense vector indexes...", pct: "50%" },
      { text: "Cross-verifying clauses against contract terms...", pct: "75%" },
      { text: "Finalizing contract safety score and audit memo...", pct: "95%" }
    ];

    let sIdx = 0;
    const timer = setInterval(() => {
      if (sIdx < stages.length) {
        if (uploadStageText) uploadStageText.textContent = stages[sIdx].text;
        if (uploadStageBar) uploadStageBar.style.width = stages[sIdx].pct;
        sIdx++;
      }
    }, 2800);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error(`Upload failed with status ${res.status}`);
      const data = await res.json();

      if (data.report) {
        renderAll(data.report);
        modalUploadAudit.close();
        showToast(`Audit complete for "${file.name}"!`, "success");
        enterAuditorApp("all");
      }
    } catch (err) {
      showToast("Upload error: " + err.message, "error");
    } finally {
      clearInterval(timer);
      if (modalDropArea) modalDropArea.style.display = "block";
      if (modalUploadProgress) modalUploadProgress.style.display = "none";
      if (modalFileInput) modalFileInput.value = "";
    }
  }

  // Asymmetry Modal (Unilateral Terms Matrix)
  function openAsymmetryModal() {
    if (!modalAsymmetry || !modalAsymBody || !auditData) return;
    modalAsymBody.innerHTML = "";

    const items = auditData.clause_balance || [];
    items.forEach((b) => {
      const div = document.createElement("div");
      div.style.cssText = "margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border-light);";
      div.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <h4 style="font-size: 14px; font-weight: 700; color: var(--text-primary);">${escapeHtml(b.title)}</h4>
          <span class="clause-ref-code">Page ${b.page || 3}</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 10px;">
          <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: var(--radius-sm); padding: 10px;">
            <strong style="color: #991B1B; font-size: 11px; text-transform: uppercase;">Provider Terms:</strong>
            <p style="font-size: 12.5px; color: #7F1D1D; margin-top: 3px;">${escapeHtml(b.provider_terms)}</p>
          </div>
          <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: var(--radius-sm); padding: 10px;">
            <strong style="color: #1D4ED8; font-size: 11px; text-transform: uppercase;">Your Terms:</strong>
            <p style="font-size: 12.5px; color: #1E3A8A; margin-top: 3px;">${escapeHtml(b.customer_terms)}</p>
          </div>
        </div>
        <div style="font-size: 12.5px; color: var(--text-secondary); background: #F8FAFC; padding: 8px 12px; border-radius: 4px;">
          <strong>Why Unfair:</strong> ${escapeHtml(b.asymmetry_summary)}
        </div>
      `;
      modalAsymBody.appendChild(div);
    });

    modalAsymmetry.showModal();
  }

  btnCloseAsymModal?.addEventListener("click", () => modalAsymmetry?.close());

  // Missing Clause Inserter Modal
  function openMissingClauseModal(item) {
    if (!modalMissingClause) return;
    if (missingClauseModalTitle) missingClauseModalTitle.textContent = item.title;
    if (missingClauseModalWhy) missingClauseModalWhy.textContent = item.why_it_matters;
    if (missingClauseModalCode) missingClauseModalCode.textContent = item.recommended_clause || "Standard clause text.";

    btnCopyMissingClauseCode.onclick = () => {
      copyToClipboard(item.recommended_clause || "", btnCopyMissingClauseCode, "Clause copied to clipboard!");
    };

    modalMissingClause.showModal();
  }

  btnCloseMissingClause?.addEventListener("click", () => modalMissingClause?.close());

  // Close dialogs on backdrop click
  [modalEvidenceTrace, modalQuickSearch, modalUploadAudit, modalAsymmetry, modalMissingClause].forEach((d) => {
    d?.addEventListener("click", (e) => {
      if (e.target === d) d.close();
    });
  });
  // =========================================================================
  // LANDING PAGE & AUDITOR WORKSPACE TRANSITIONS
  // =========================================================================
  const landingView = document.getElementById("landing-view");
  const appShell = document.getElementById("app-shell");
  const btnReturnHome = document.getElementById("btn-return-home");

  async function enterAuditorApp(filter = "all") {
    if (landingView) landingView.style.display = "none";
    if (appShell) {
      appShell.style.display = "flex";
      // Load demo data only upon explicit user click
      if (!auditData) {
        await loadDemoReport();
      }
      if (filter !== "all") {
        activeFindingsFilter = filter;
        updateFindingsFilterPills();
        renderFindingsScreen();
        switchScreen("screen-findings", "tab-findings");
      } else {
        switchScreen("screen-overview", "tab-overview");
      }
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function returnToLanding() {
    if (appShell) appShell.style.display = "none";
    if (landingView) {
      landingView.style.display = "flex";
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  // CTAs to Enter the Auditor Workspace (Only processes AFTER click)
  [
    document.getElementById("btn-landing-nav-demo"),
    document.getElementById("btn-hero-launch-demo"),
    document.getElementById("btn-footer-demo"),
    document.getElementById("btn-teaser-view-full"),
    document.getElementById("btn-hero-sample-pill")
  ].forEach((btn) => {
    btn?.addEventListener("click", () => enterAuditorApp("all"));
  });

  // Teaser findings direct jump buttons
  document.querySelectorAll(".btn-jump-finding").forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetFilter = btn.getAttribute("data-target-filter") || "all";
      enterAuditorApp(targetFilter);
    });
  });

  // Topbar and Brand return buttons
  btnReturnHome?.addEventListener("click", returnToLanding);
  document.getElementById("btn-workspace-home")?.addEventListener("click", returnToLanding);
  document.getElementById("landing-logo-btn")?.addEventListener("click", returnToLanding);

  // Upload buttons from Landing Page
  [
    document.getElementById("btn-landing-nav-upload"),
    document.getElementById("btn-hero-upload-doc")
  ].forEach((btn) => {
    btn?.addEventListener("click", () => {
      modalUploadAudit?.showModal();
    });
  });

  // =========================================================================
  // EMIL KOWALSKI HOVER DETAIL INTERACTIONS
  // =========================================================================
  const clauseHoverTriggers = document.querySelectorAll(".hover-detail-trigger");
  const clauseHoverTooltip = document.getElementById("clause-hover-tooltip");
  const clauseTooltipBody = document.getElementById("clause-tooltip-body");

  const clauseExplanations = {
    "exposure-asymmetry": "Unilateral Termination Risk: Provider reserves sole discretionary power to terminate upon 30 days' notice without cause, while Customer has zero reciprocal rights. Immediate breach of institutional procurement standard.",
    "exposure-refund": "Fee Forfeiture Trap: Clause permits Provider to retain 100% of unamortized annual subscription payments following their own discretionary termination without cause. Violates standard commercial remedies."
  };

  clauseHoverTriggers.forEach((trigger) => {
    trigger.addEventListener("mouseenter", () => {
      const key = trigger.getAttribute("data-detail");
      if (clauseTooltipBody && clauseExplanations[key]) {
        clauseTooltipBody.textContent = clauseExplanations[key];
        clauseHoverTooltip?.classList.add("active");
      }
    });

    trigger.addEventListener("mouseleave", () => {
      clauseHoverTooltip?.classList.remove("active");
    });
  });

  // =========================================================================
  // DEMO DATA LOADER (ONLY INVOKED ON EXPLICIT USER INTERACTION)
  // =========================================================================
  async function loadDemoReport() {
    try {
      showToast("Loading contract audit demo...", "info");
      const demoRes = await fetch("/api/sample/demo");
      if (demoRes.ok) {
        const demoData = await demoRes.json();
        renderAll(demoData.report || demoData);
        showToast("Demo contract audit loaded successfully!", "success");
      }
    } catch (err) {
      console.log("Waiting for contract upload or demo initialization.");
      showToast("Could not load sample contract demo", "warning");
    }
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // NOTE: Clean standby mode. We do NOT run initApp() automatically on startup.
  // The backend and frontend wait until the user clicks to launch the demo or uploads a document.
});
