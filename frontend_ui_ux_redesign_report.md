# TIERFLOW — Frontend UI/UX Audit and Redesign Report

**Date:** November 25, 2026  
**Product:** TIERFLOW — Adaptive LLM Inference Platform  
**Live Site:** [https://tierflow-ruddy.vercel.app/](https://tierflow-ruddy.vercel.app/)  
**Repository:** `tanmay-madaan/tierflow` (Frontend Directory: `frontend/`)  
**Lead Engineer & Designer:** Senior Product Designer & Frontend Engineer (Autonomous Systems)

---

## 1. Executive Summary

A comprehensive UI/UX audit and complete frontend redesign of the TIERFLOW platform was executed. The platform has been transformed from an early prototype dashboard into a polished, professional, research-grade developer observability and adaptive routing platform suitable for demonstration to university professors, technical reviewers, and industry engineering teams.

All improvements were completed directly inside the existing frontend codebase (`frontend/`) without breaking existing functionality, modifying backend routing algorithms, or altering experimental datasets.

---

## 2. Pages Inspected & Problems Identified (Phase 1 Audit)

Live webview inspection of https://tierflow-ruddy.vercel.app/ was performed across four viewports:
- **Desktop (1440×900)**
- **Laptop (1280×800)**
- **Tablet (768×1024)**
- **Mobile (390×844)**

### 2.1 Critical Architectural & Layout Defects
1. **Broken Direct SPA Navigation on Vercel:**  
   Direct links or browser refreshes to `/playground`, `/experiments`, or `/research` triggered a `404: NOT_FOUND` error because the deployment lacked a `vercel.json` SPA rewrite configuration.
2. **Mobile & Tablet Viewport Collapse:**  
   The layout utilized a rigid `w-64` desktop sidebar without responsive collapsing. On tablet (768px), the main viewport was squeezed to 512px; on mobile (390px), the sidebar occupied 256px, forcing the main canvas into 134px and causing extreme horizontal clipping.
3. **Misleading Telemetry Presentations on Overview:**  
   When data was unavailable or zero, the Overview displayed `0.00s` latency with a green upward improvement arrow `↑ vs 2.80s Always-Large` and `+0.0%` cost reduction with an affirmative "Token Savings" badge. The charts showed `-0.0%` or empty circles without empty-state messaging.
4. **Sub-optimal Playground Layout:**  
   The Playground was rendered as a single vertical column on desktop, leaving half of the 1440px viewport blank, while sample prompt chips were forced into awkward horizontal scrolling. The multi-stage routing pipeline was absent.
5. **Experiment Log Filtering & Audit Deficiencies:**  
   The experiment log only supported a single tier dropdown filter and lacked counters for Total, Real, Demo, Success, and Error counts. Table records lacked timestamp, run ID, and explicit execution mode badges.
6. **Stale Benchmark Data on Research Page:**  
   Section 2 presented an obsolete 3-policy comparison based on an old 4-prompt demo smoke test (`run_98c7abfb`), claiming `p < 0.001` statistical significance on $N=4$ demo prompts while omitting `ALWAYS_SMALL` and `ALWAYS_MEDIUM`. The mandatory evidence classification distinguishing real API runs from simulated software demos was missing.

---

## 3. Visual Design System (Phase 2 Implementation)

The interface was standardized to a dark AI infrastructure observability aesthetic:

### 3.1 Color Tokens (`tailwind.config.js` & `index.css`)
- **Main Canvas:** `#0B0F14` (Deep obsidian)
- **Surface Layer:** `#141E2A` (Rich slate blue)
- **Secondary Surface:** `#101722` (Dark panel backdrop)
- **Elevated Surface:** `#192536` (Raised card container)
- **Default Borders:** `#263548` (Technical slate border)
- **Subtle Borders:** `#1E2A39`
- **Primary Text:** `#F1F5F9` (High-contrast slate white)
- **Secondary Text:** `#A0AEC0`
- **Muted Text:** `#718096`
- **Primary Accent:** `#3B82F6` (Electric Blue)

### 3.2 Model Tier Color System
- **SMALL:** `#34D399` (Emerald Green)
- **MEDIUM:** `#F59E0B` (Technical Amber)
- **LARGE:** `#818CF8` (Soft Indigo)

### 3.3 Execution Mode Badges
- **REAL / LIVE API:** Green dot with subtle pulse (`#34D399`)
- **DEMO / SIMULATED:** Neutral blue dot (`#3B82F6`)
- **PROJECTED ESTIMATE:** Amber dot (`#F59E0B`)
- **ERROR / FAILED:** Red dot (`#EF4444`)

### 3.4 Shared Components Created
- `ModelBadge.jsx`: Standardized model tier badge with consistent sizing (`sm`, `lg`) and dot tokens.
- `ExecutionModeBadge.jsx`: Unmistakable visual indicator for live vs simulated data.
- `StatCard.jsx`: Metric card with large readable typography, data-source tags, and graceful fallback to `N/A` without misleading green trend arrows.
- `PageHeader.jsx`: Unified page header with titles, subtitles, and status pills.
- `EmptyState.jsx`: Clean informative empty states for charts, tables, and search results.
- `CustomTooltip.jsx`: High-contrast dark engineering tooltip for Recharts visualizations.
- `PipelineFlow.jsx`: Visual 6-stage routing pipeline component with active tier highlighting.

---

## 4. Page Redesigns (Phase 3 Implementation)

### 4.1 Page 1: Overview (`/`)
- **Header:** Added system status pill (Live Mode vs Demo Mode), provider tag (`Google Gemini`), and quick link to Playground.
- **KPIs:** Redesigned 4 primary stat cards with explicit data-source indicators (`Measured`, `Simulated`, `Evaluator`). Gracefully displays `N/A` when no queries have been processed instead of `0.00s` or `+0.0%`.
- **Quick Route Inspector:** Replaced single-line input with a multi-line prompt textarea featuring live word and character counters. Added prominent selected tier badge, confidence score, complexity rating, and routing rationale.
- **Telemetry Charts:** Enhanced Pie and Bar charts with actual counts, percentages, and Recharts tooltips. Added empty states when zero session queries exist.
- **Research Summary:** Compact 3-card architectural overview detailing Small (`gemini-3.5-flash-lite`), Medium (`gemini-flash-latest`), and Large (`gemini-pro-latest`) pricing and target workloads.

### 4.2 Page 2: Playground (`/playground`)
- **Two-Part Layout:** 
  - Left column (7 cols on desktop): Prompt textarea with word/char counters, clear/reset button, sample prompt chips, keyboard shortcut (`⌘/Ctrl+Enter`), and distinct actions: **Predict Route** (lightweight classifier) vs **Run Inference** (model execution).
  - Right column (5 cols on desktop): Dedicated routing decision console displaying selected tier, target model ID, confidence, complexity, latency, estimated cost, and rationale.
- **Interactive Pipeline:** Implemented `PipelineFlow` displaying:  
  `USER QUERY → FEATURE EXTRACTION → ML CLASSIFIER → MODEL TIER SELECTION → LLM INFERENCE → RESPONSE`.
- **Softmax Probabilities:** Dynamic horizontal progress bars reflecting actual backend probabilities from `routingResult.probabilities` using standardized tier colors.
- **Linguistic Features:** 9-cell grid showing word count, characters, sentences, keyword detections (math, code, reasoning), constraints, and multi-step indicators.
- **Response Panel:** Clean monospaced response viewer with one-click copy, token usage breakdown (prompt, completion, total), and latency/cost deltas.

### 4.3 Page 3: Experiment Log (`/experiments`)
- **Summary Counters:** Added top summary strip displaying: Total Logged, Live Provider, Simulated Demo, Successful, and Failed requests.
- **Multi-Filter Toolbar:** Independent and combined filtering by:
  - Text search (query, model ID, response content)
  - Model Tier (`ALL`, `SMALL`, `MEDIUM`, `LARGE`)
  - Execution Mode (`ALL`, `REAL`, `DEMO`)
  - Status (`ALL`, `SUCCESS`, `FAILED`)
- **Redesigned Audit Table:** Added Mode badge, timestamp, complexity, latency, cost, quality score, and status badge.
- **Expanded Audit Drawer:** Clicking any row reveals a comprehensive diagnostic panel with full prompt, generated output, record ID, model ID, confidence, token counts, and error details with copy actions.

### 4.4 Page 4: Benchmark & Eval (`/research`)
- **Section 1: Classifier Evaluation:** Held-out test accuracy (87.8%), macro precision (88.7%), macro recall (89.8%), macro F1 (88.9%), and multiclass confusion matrix with clear diagonal/off-diagonal styling.
- **Section 2: Five-Policy Routing Comparison:** 
  - Master evaluation table incorporating all 5 policies: `ALWAYS_SMALL`, `ALWAYS_MEDIUM`, `ALWAYS_LARGE`, `ADAPTIVE_ML`, and `RULE_BASED`.
  - Established Benchmark v2 ($N=200$) allocations: Small (100%), Medium (100%), Large (100%), Adaptive ML (16% S / 24% M / 60% L), Rule-Based (26.5% S / 51% M / 22.5% L).
  - Horizontal stacked bar chart visualization.
- **Section 3: Mandatory Evidence Classification:** Explicit classification distinguishing the genuine, measured real API benchmark of `ALWAYS_SMALL` ($N=200$, 199 successful, 1 rate-limit failure, 7.9291/10 quality, 1.455s latency, $0.087601 cost) from the demo-mode software validations of the remaining policies.
- **Section 4: Cost Comparison (Actual vs Projected):** Visually separated measured cost ($0.087601 for Small) from projected estimates based on measured token usage: Medium ($0.1342), Large ($0.4258), Adaptive ML ($0.2560), and Rule-Based ($0.1754).
- **Section 5: Architectural Routing Analysis:** Tabbed category and difficulty breakdown explaining why Adaptive ML routes 60% to Large (length and reasoning vocabulary dominance) vs Rule-Based centering on Medium (51%).
- **Section 6: Methodology & Limitations:** Collapsible section detailing dataset SHA-256, single-turn 512-token ceiling, free-tier Pro quota realities, and evaluator bounds.
- **Demo Smoke Test:** Relabeled the quick benchmark trigger to "Run Demo Smoke Test (5 Items)" to prevent confusion with the full 200-prompt empirical evaluation.

---

## 5. Responsive Design & Accessibility Audit (Phase 4)

- **Mobile Navigation Drawer:** Added an off-canvas responsive drawer with dark backdrop on screens `< 1024px` (`lg` breakpoint). Replaced rigid sidebar with a slim mobile topbar containing brand header and hamburger button.
- **No Horizontal Page Overflow:** Enforced `overflow-x-hidden` on body and container wrappers. Tables wrap cleanly with horizontal internal scrollbars (`min-w-[760px]`).
- **Keyboard Navigation & Accessibility:** Implemented visible focus rings (`focus-visible:outline-2 focus-visible:outline-[#3B82F6]`) and semantic heading structures across all pages.
- **Vercel Deep-Linking:** Added `vercel.json` rewrites so direct navigation to `/playground`, `/experiments`, and `/research` routes correctly resolves to `index.html`.

---

## 6. Functional Regression Audit (Phase 5)

| Functional Area | Verification Status | Notes |
| :--- | :---: | :--- |
| **Backend Routing Algorithms** | **Unmodified** | Classifier, thresholds, feature extractors untouched. |
| **Model Selection Logic** | **Unmodified** | Providers and escalation thresholds intact. |
| **Benchmark Datasets & DB** | **Unmodified** | All 240+ SQLite records and Benchmark v2 JSON preserved. |
| **Route Prediction (`/route`)** | **Verified** | Predict Route returns tier, confidence, complexity, features. |
| **Demo Inference (`/query`)** | **Verified** | Offline simulation works seamlessly with latency/cost metrics. |
| **Live API Mode (`/query`)** | **Verified** | Gracefully reports missing API key / quota errors without crashing. |
| **Experiments Multi-Filter** | **Verified** | Search, tier, mode, and status filters work together. |
| **Clipboard Copy Actions** | **Verified** | Feedback state toggles to "Copied" with green checkmark. |
| **Smoke Test Execution** | **Verified** | Ephemeral 5-item test completes without altering primary data. |

---

## 7. Production Build Verification (Phase 6)

```bash
> frontend@0.0.0 build
> vite build

vite v5.4.21 building for production...
transforming...
✓ 2207 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.79 kB │ gzip:   0.47 kB
dist/assets/index-WLjlo1w6.css   22.18 kB │ gzip:   5.03 kB
dist/assets/index-DNX0pB4P.js   678.12 kB │ gzip: 186.43 kB
✓ built in 7.16s
```

**Build Status:** Clean production build with exit code `0`. Zero TypeScript, JSX, or CSS compilation errors.

---

## 8. Summary of Files Modified & Created

### Modified Files:
- `frontend/src/App.jsx`
- `frontend/src/components/ModelBadge.jsx`
- `frontend/src/components/StatCard.jsx`
- `frontend/src/index.css`
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/pages/RouterPlayground.jsx`
- `frontend/src/pages/Experiments.jsx`
- `frontend/src/pages/ResearchResults.jsx`
- `frontend/tailwind.config.js`

### Created Files:
- `frontend/src/components/ExecutionModeBadge.jsx`
- `frontend/src/components/PageHeader.jsx`
- `frontend/src/components/EmptyState.jsx`
- `frontend/src/components/CustomTooltip.jsx`
- `frontend/src/components/PipelineFlow.jsx`
- `frontend/src/data/benchmarkData.js`
- `frontend/vercel.json`
- `vercel.json`

---
*Report generated and approved by Antigravity Autonomous Systems.*
