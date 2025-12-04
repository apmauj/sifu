# Frontend Architecture

## Overview

The SIFU frontend follows a **hexagonal/clean architecture** pattern that mirrors the backend structure. This provides:

- **Separation of concerns**: Business logic is isolated in feature modules
- **Testability**: Each layer can be tested independently
- **Maintainability**: Clear boundaries make code easier to understand and modify
- **Scalability**: New features can be added without affecting existing code

## Directory Structure

```
frontend/src/
├── app/                    # Application shell
│   ├── AppProviders.jsx    # Context providers wrapper
│   ├── ErrorBoundary.jsx   # Error handling component
│   └── index.js            # App module exports
│
├── features/               # Feature modules (domain logic)
│   ├── brou/              # BROU rates feature
│   │   ├── BROUPanel.jsx
│   │   └── index.js
│   ├── dashboard/         # System dashboard feature
│   │   ├── Dashboard.jsx
│   │   └── index.js
│   ├── exchange/          # Exchange rates feature
│   │   ├── ExchangeDataStatusPanel.jsx
│   │   ├── ExchangeRatePanel.jsx
│   │   ├── ExchangeResultsDisplay.jsx
│   │   ├── ExchangeSearchForm.jsx
│   │   └── index.js
│   ├── monitoring/        # Monitoring access feature
│   │   ├── MonitoringAccess.jsx
│   │   ├── MonitoringAccess.css
│   │   └── index.js
│   ├── ui/               # UI (inflation) feature
│   │   ├── ResultsDisplay.jsx
│   │   ├── SearchForm.jsx
│   │   ├── UIPanel.jsx
│   │   └── index.js
│   ├── ur/               # UR (reserve unit) feature
│   │   ├── URPanel.jsx
│   │   ├── URResultsDisplay.jsx
│   │   ├── URSearchForm.jsx
│   │   └── index.js
│   └── index.js          # Re-exports all features
│
├── shared/                # Shared infrastructure
│   ├── components/        # Reusable UI components
│   │   ├── icons/        # Icon components
│   │   ├── ui/           # Base UI components (Card, Tabs, etc.)
│   │   ├── Header.jsx
│   │   ├── BuildInfoFooter.jsx
│   │   ├── LanguageSelector.jsx
│   │   ├── QuickSelectors.jsx
│   │   └── ToastNotification.jsx
│   ├── contexts/          # React contexts
│   │   ├── I18nContext.jsx
│   │   ├── ThemeContext.jsx
│   │   └── ToastContext.jsx
│   ├── hooks/             # Shared React hooks
│   │   ├── useHourlySyncedUpdate.js
│   │   └── ...
│   ├── icons/             # Icon assets and components
│   │   ├── openmoji/     # OpenMoji icons
│   │   ├── flags/        # Country flags
│   │   └── system_icons.js
│   ├── locales/           # i18n translations
│   │   ├── en.json
│   │   ├── es.json
│   │   └── pt.json
│   ├── services/          # API services
│   │   ├── api.js        # Base API client (UI service)
│   │   ├── brouService.js
│   │   ├── exchangeService.js
│   │   ├── healthService.js
│   │   ├── performanceService.js
│   │   ├── urService.js
│   │   └── index.js
│   ├── theme/             # Theme configuration
│   │   ├── colors.js
│   │   ├── themes.js
│   │   └── themeUtils.js
│   ├── utils/             # Utility functions
│   │   ├── apiConfig.js
│   │   ├── dateUtils.js
│   │   └── ...
│   └── index.js           # Shared module exports
│
├── test/                   # Test files
│   ├── architecture/      # Architecture validation tests
│   ├── components/        # Component tests
│   ├── services/          # Service tests
│   └── ...
│
├── App.jsx                # Main application component
├── main.jsx               # Application entry point
├── index.css              # Global styles
└── constants.js           # Application constants
```

## Layer Responsibilities

### App Layer (`app/`)
- Application bootstrapping
- Context provider composition
- Global error handling
- Entry point configuration

### Features Layer (`features/`)
- **Domain-specific components**: Each feature contains components specific to its domain
- **Self-contained**: Features can import from `shared/` but not from other features
- **Index exports**: Each feature has an `index.js` for clean imports

### Shared Layer (`shared/`)
- **Reusable components**: UI components used across multiple features
- **Infrastructure**: Contexts, hooks, services, utilities
- **No domain logic**: Shared code should be generic and reusable

## Import Patterns

### Feature to Shared
```jsx
// Inside a feature component
import { useI18n } from '../../shared/contexts/I18nContext';
import exchangeService from '../../shared/services/exchangeService';
import { LoadingIcon } from '../../shared/components/icons/SimpleIcons';
```

### App to Features
```jsx
// In App.jsx
import { UIPanel } from './features/ui';
import { ExchangeRatePanel } from './features/exchange';
import { Dashboard } from './features/dashboard';
```

### App to Shared
```jsx
// In App.jsx
import Header from './shared/components/Header';
import { useI18n } from './shared/contexts/I18nContext';
import exchangeService from './shared/services/exchangeService';
```

## Testing Strategy

Tests are organized in `src/test/` mirroring the source structure:
- `test/components/` - Feature component tests
- `test/services/` - Service tests
- `test/hooks/` - Hook tests
- `test/architecture/` - Architecture validation (i18n parity, etc.)

## Migration Notes

This architecture was implemented in the `feature/frontend-architecture-v1` branch with the following stages:

1. **Stage 1**: Created `app/`, `features/`, `shared/` folders and extracted ErrorBoundary
2. **Stage 2**: Moved shared components to `shared/` (Header, Footer, contexts, hooks, icons, theme, utils, locales)
3. **Stage 3**: Moved feature components to `features/` (UI, UR, Exchange, BROU, Dashboard, Monitoring)
4. **Stage 4**: Moved services to `shared/services/`
5. **Stage 5-6**: Cleaned up old folders
6. **Stage 7-8**: Updated imports and documentation

All 627 tests pass after reorganization.
