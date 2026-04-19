# ADR-0001 - Layer Boundaries and Dependency Rules

Status: Accepted
Date: 2026-04-19
Scope: Backend architecture in src/

## Context

SIFU already uses a layered structure under src/:

- src/api
- src/application
- src/domain
- src/infrastructure
- src/utils

Over time, cross-layer imports can drift and increase coupling. We need explicit dependency rules and automated checks to keep architecture stable while evolving features.

## Decision

Define and enforce layer dependency rules.

Allowed imports by layer:

1. api
- Allowed: api, application, domain, infrastructure, utils
- Rationale: API orchestrates request flow and can wire services and adapters.

2. application
- Allowed: application, domain, infrastructure, utils
- Rationale: application coordinates use cases and operational concerns.

3. domain
- Allowed: domain, utils
- Rationale: domain must remain mostly pure and stable.

4. infrastructure
- Allowed: infrastructure, domain, utils
- Rationale: infrastructure adapts external systems and may depend on domain contracts.

5. utils
- Allowed: utils
- Rationale: utils is foundational and must not depend on upper layers.

Prohibited examples:

- domain -> infrastructure/application/api
- utils -> any upper layer
- infrastructure -> application/api
- application -> api

## Consequences

Positive:

1. Reduced coupling and clearer ownership per layer.
2. Better refactor safety and easier testing.
3. Architectural drift becomes measurable.

Trade-offs:

1. Existing violations may require staged cleanup.
2. Some pragmatic exceptions may be needed temporarily.

## Enforcement

1. Script: scripts/architecture/check_layer_imports.ps1
2. CI mode strategy:
- Phase 0: warn mode (non-blocking), publish report.
- Later phase: fail mode (blocking) once violations are reduced.

## Rollout plan

1. Generate baseline report and capture current violations.
2. Prioritize high-frequency edges first.
3. Flip CI from warn to fail when backlog is under agreed threshold.
