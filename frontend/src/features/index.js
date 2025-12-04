/**
 * Features module
 * 
 * Each feature is a self-contained module with its own:
 * - components
 * - index.js (public exports)
 * 
 * Features:
 * - ui: Unidad Indexada (UI) feature
 * - ur: Unidad Reajustable (UR) feature
 * - exchange: Exchange rates feature
 * - brou: BROU current rates feature
 * - dashboard: Monitoring dashboard feature
 * - monitoring: System monitoring access feature
 */

// Feature exports
export * from './ui';
export * from './ur';
export * from './exchange';
export * from './brou';
export * from './dashboard';
export * from './monitoring';
// export * from './exchange';
// export * from './brou';
// export * from './dashboard';
