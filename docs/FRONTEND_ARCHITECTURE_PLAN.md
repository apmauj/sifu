# Frontend Architecture Reorganization Plan

**Branch:** `feature/frontend-architecture-v1`  
**Date:** 2025-12-04  
**Status:** 🚧 In Progress  
**Estimated Duration:** 2-3 sessions  
**Risk Level:** Medium (many imports to update, but well-tested features)

---

## 📋 Objective

Reorganize the frontend from a flat structure to a **feature-based architecture** that mirrors the backend's hexagonal pattern, improving maintainability, testability, and developer experience.

---

## 🔍 Current State Analysis

### Problems Identified:

| Issue | Severity | Evidence |
|-------|----------|----------|
| **God Component** | 🔴 High | `App.jsx` has 575 lines handling all features |
| **Flat structure** | 🟡 Medium | 31 components in single `components/` folder |
| **Mixed concerns** | 🟡 Medium | Exchange polling logic in App.jsx |
| **No feature isolation** | 🟡 Medium | Hard to find related code |
| **Inconsistent with backend** | 🟡 Medium | Backend is hexagonal, frontend is flat |

### Current Structure:
```
frontend/src/
├── App.jsx                 # 575 lines - GOD COMPONENT
├── main.jsx
├── components/             # 31 files, flat
│   ├── UIPanel.jsx
│   ├── URPanel.jsx
│   ├── ExchangeRatePanel.jsx
│   ├── BROUPanel.jsx
│   ├── Dashboard.jsx
│   ├── Header.jsx
│   └── ... (25 more)
├── services/               # Well organized (7 files)
├── contexts/               # 3 contexts
├── hooks/                  # 3 hooks
├── theme/                  # Theme system
├── locales/                # i18n
└── utils/                  # Utilities
```

---

## 🎯 Target Structure

```
frontend/src/
├── app/                           # Application shell
│   ├── App.jsx                    # ~100-150 lines (routing + layout only)
│   ├── AppProviders.jsx           # All context providers wrapped
│   ├── ErrorBoundary.jsx          # Extracted from App.jsx
│   └── routes.js                  # Route definitions (if needed later)
│
├── features/                      # Feature modules (domain-driven)
│   ├── ui/                        # UI (Unidad Indexada) feature
│   │   ├── components/
│   │   │   ├── UIPanel.jsx
│   │   │   ├── UISearchForm.jsx   # Extracted from SearchForm
│   │   │   └── UIResultsDisplay.jsx
│   │   ├── hooks/
│   │   │   └── useUIData.js       # UI-specific data fetching logic
│   │   ├── services/
│   │   │   └── uiService.js       # Moved from services/api.js
│   │   └── index.js               # Public exports
│   │
│   ├── ur/                        # UR (Unidad Reajustable) feature
│   │   ├── components/
│   │   │   ├── URPanel.jsx
│   │   │   ├── URSearchForm.jsx
│   │   │   └── URResultsDisplay.jsx
│   │   ├── hooks/
│   │   │   └── useURData.js
│   │   ├── services/
│   │   │   └── urService.js
│   │   └── index.js
│   │
│   ├── exchange/                  # Exchange rates feature
│   │   ├── components/
│   │   │   ├── ExchangePanel.jsx  # Container for exchange feature
│   │   │   ├── ExchangeRatePanel.jsx
│   │   │   ├── ExchangeSearchForm.jsx
│   │   │   ├── ExchangeResultsDisplay.jsx
│   │   │   └── ExchangeDataStatusPanel.jsx
│   │   ├── hooks/
│   │   │   ├── useExchangeData.js      # State + fetching
│   │   │   └── useExchangePolling.js   # Job polling logic
│   │   ├── services/
│   │   │   └── exchangeService.js
│   │   └── index.js
│   │
│   ├── brou/                      # BROU feature
│   │   ├── components/
│   │   │   └── BROUPanel.jsx
│   │   ├── hooks/
│   │   │   └── useBROUData.js
│   │   ├── services/
│   │   │   └── brouService.js
│   │   └── index.js
│   │
│   └── dashboard/                 # Dashboard/Monitoring feature
│       ├── components/
│       │   ├── Dashboard.jsx
│       │   └── MonitoringAccess.jsx
│       ├── hooks/
│       │   └── useMonitoringSession.js
│       ├── services/
│       │   ├── healthService.js
│       │   └── performanceService.js
│       └── index.js
│
├── shared/                        # Shared/common code
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── BuildInfoFooter.jsx
│   │   ├── QuickSelectors.jsx
│   │   ├── ToastNotification.jsx
│   │   ├── LanguageSelector.jsx
│   │   └── ui/                    # Generic UI primitives
│   │       ├── Card.jsx
│   │       ├── Tabs.jsx
│   │       ├── Button.jsx
│   │       └── ...
│   ├── contexts/
│   │   ├── I18nContext.jsx
│   │   ├── ThemeContext.jsx
│   │   └── ToastContext.jsx
│   ├── hooks/
│   │   ├── useHourlySyncedUpdate.js
│   │   └── useApiHealth.js
│   ├── services/
│   │   └── api.js                 # Base API client (axios setup)
│   ├── utils/
│   │   ├── apiConfig.js
│   │   ├── colors.js
│   │   └── ...
│   ├── theme/
│   │   └── ...
│   ├── locales/
│   │   └── ...
│   └── icons/
│       └── ...
│
├── constants.js                   # App-wide constants
├── index.css                      # Global styles
└── main.jsx                       # Entry point
```

---

## 📦 Migration Stages

### Stage 1: Setup Structure & Extract ErrorBoundary
**Risk:** ⭐ Very Low  
**Changes:**
- Create folder structure (`app/`, `features/`, `shared/`)
- Extract `ErrorBoundary` from App.jsx to `app/ErrorBoundary.jsx`
- Create `app/AppProviders.jsx` wrapping all context providers
- **Tests must pass**

### Stage 2: Move Shared Components
**Risk:** ⭐ Low  
**Changes:**
- Move `Header.jsx` → `shared/components/Header.jsx`
- Move `BuildInfoFooter.jsx` → `shared/components/`
- Move `QuickSelectors.jsx` → `shared/components/`
- Move `ToastNotification.jsx` → `shared/components/`
- Move `LanguageSelector.jsx` → `shared/components/`
- Move `ui/` folder → `shared/components/ui/`
- Move `contexts/` → `shared/contexts/`
- Move `hooks/` → `shared/hooks/`
- Move `utils/` → `shared/utils/`
- Move `theme/` → `shared/theme/`
- Move `locales/` → `shared/locales/`
- Move `icons/` → `shared/icons/`
- Update all imports
- **Tests must pass**

### Stage 3: Extract UI Feature
**Risk:** ⭐⭐ Low-Medium  
**Changes:**
- Create `features/ui/` structure
- Move `UIPanel.jsx` → `features/ui/components/`
- Extract UI logic from App.jsx into `useUIData.js` hook
- Move UI service methods to `features/ui/services/uiService.js`
- Create `features/ui/index.js` exports
- Update App.jsx to use the new hook
- **Tests must pass**

### Stage 4: Extract UR Feature
**Risk:** ⭐⭐ Low-Medium  
**Changes:**
- Create `features/ur/` structure
- Move `URPanel.jsx`, `URSearchForm.jsx`, `URResultsDisplay.jsx`
- Extract UR logic into `useURData.js` hook
- Move `urService.js` → `features/ur/services/`
- **Tests must pass**

### Stage 5: Extract Exchange Feature (Most Complex)
**Risk:** ⭐⭐⭐ Medium  
**Changes:**
- Create `features/exchange/` structure
- Move all Exchange components
- Extract exchange state and logic from App.jsx:
  - `useExchangeData.js` - state management
  - `useExchangePolling.js` - job polling logic
- Move `exchangeService.js` → `features/exchange/services/`
- This is the biggest extraction (~200 lines from App.jsx)
- **Tests must pass**

### Stage 6: Extract BROU Feature
**Risk:** ⭐⭐ Low-Medium  
**Changes:**
- Create `features/brou/` structure
- Move `BROUPanel.jsx`
- Move `brouService.js`
- **Tests must pass**

### Stage 7: Extract Dashboard Feature
**Risk:** ⭐⭐ Low-Medium  
**Changes:**
- Create `features/dashboard/` structure
- Move `Dashboard.jsx`, `MonitoringAccess.jsx`
- Extract monitoring session logic to `useMonitoringSession.js`
- Move `healthService.js`, `performanceService.js`
- **Tests must pass**

### Stage 8: Cleanup & Final App.jsx
**Risk:** ⭐ Low  
**Changes:**
- Refactor App.jsx to use feature hooks
- App.jsx should be ~100-150 lines (layout + tab routing)
- Remove old files and empty folders
- Update any remaining imports
- **Full test suite + manual testing**

---

## ✅ Acceptance Criteria

| Criterion | Evidence |
|-----------|----------|
| All tests pass | `npm test` green |
| Vite build succeeds | `npm run build` no errors |
| App.jsx ≤ 150 lines | Line count check |
| Each feature is self-contained | Can find all UI code in `features/ui/` |
| No circular dependencies | Build warns if any |
| No functionality regression | Manual testing of all tabs |

---

## 🔙 Rollback Strategy

- Each stage is a separate commit
- If a stage breaks tests, revert that commit
- Branch isolates all changes from master
- Only merge when 100% validated

---

## 📝 Notes

- Keep backward compatibility during migration
- Use barrel exports (`index.js`) for clean imports
- Consider lazy loading features in future (code splitting)
- Document any breaking changes to component APIs

---

## 📅 Progress Tracking

| Stage | Status | Date | Notes |
|-------|--------|------|-------|
| Stage 1 | ⏳ Pending | - | - |
| Stage 2 | ⏳ Pending | - | - |
| Stage 3 | ⏳ Pending | - | - |
| Stage 4 | ⏳ Pending | - | - |
| Stage 5 | ⏳ Pending | - | - |
| Stage 6 | ⏳ Pending | - | - |
| Stage 7 | ⏳ Pending | - | - |
| Stage 8 | ⏳ Pending | - | - |
