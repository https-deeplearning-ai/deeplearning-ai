# Phase 1 Requirements — Hello Hono

## Scope

Install and configure Hono with a `tsx` dev server. Expose a single `/` route that renders a minimal HTML home page via Hono JSX. Confirm TypeScript types work end-to-end.

## Out of Scope

- No shared layout or navigation (Phase 2)
- No Vitest tests written for this phase (framework is installed; tests begin in Phase 2)
- No database or additional routes
- No CI/CD pipeline

## Decisions

### Pin Hono version
Record the exact Hono version in `package.json` with no range prefix (e.g., `"hono": "4.x.y"`). Future phases must not silently upgrade without deliberate review.

### Enforce strict TypeScript
`tsconfig.json` must include `"strict": true`. This is non-negotiable from the first commit so the codebase never accumulates loose types.

### Mobile-first responsive design
All CSS must be written mobile-first: base styles target small screens; `min-width` media queries enhance for larger viewports. CSS custom properties must be used for spacing and color tokens. The `<meta name="viewport">` tag must be present in the layout. This baseline applies to every phase — responsive design is never deferred.

## Context

This phase exists to prove the baseline works: Node runs TypeScript, Hono serves a response, and the dev loop is functional. Nothing more.

The home page should render an `<h1>` containing "AgentClinic" and a short tagline that reflects the mission. The route returns HTML, not a plain string — Hono JSX handles the rendering.

This is the first visible page a developer sees when they clone and run the project.

## Stakeholder Notes

- **Mary** needs TypeScript end-to-end (satisfied by `strict: true` + successful `tsc --noEmit`)
- **Steve** requires responsive design on modern browsers — satisfied by mobile-first CSS with viewport meta tag from this phase forward
