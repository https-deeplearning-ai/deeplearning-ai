# Requirements — MVP (Phases 3–7)

## Scope

The MVP delivers a fully functional AgentClinic: therapies catalog, appointment booking, staff dashboard, and a polished, hardened application ready for demo use. Phases 1 and 2 are already complete and merged.

## Phases Included

### Phase 3 — Therapies Catalog
- `therapies` table and seed data (evidence-based fictional therapies).
- `/therapies` list page.
- Many-to-many mapping: ailments → recommended therapies (join table `ailment_therapies`).
- Ailment detail (or list) surfaces recommended therapies.

### Phase 4 — Appointment Booking
- `appointments` table: `agent_id`, `therapist` (name/text), `datetime`, `status` (`pending`, `confirmed`, `cancelled`).
- Booking form on the agent detail page (`/agents/:id`).
- Server-side validation (required fields, valid datetime).
- Confirmation page after successful booking.

### Phase 5 — Staff Dashboard
- `GET /dashboard` — summary counts: total agents, open appointments, ailments currently in-flight.
- Simple table views for staff to browse and manage records.
- Satisfies the "Mary wants a nice dashboard" requirement from the mission.

### Phase 6 — Polish & Accessibility
- Responsive layout audit across all pages added in Phases 3–5.
- Semantic HTML audit (landmarks, headings, lists).
- Keyboard navigation and visible focus styles on all interactive elements.

### Phase 7 — Hardening
- Error pages: 404 (not found) and 500 (internal server error).
- Input sanitization on all forms (appointment booking).
- Basic logging middleware (request method, path, status code, duration).

## Decisions

- Follow the patterns established in Phase 2: migrations as plain `.sql` files, seeds as idempotent TypeScript scripts, routes as Hono routers, components as server-side JSX.
- No new dependencies beyond what Phase 2 introduced unless strictly necessary.
- CSS continues to use PicoCSS + a supplemental `styles.css`; no new CSS framework.
- Therapist is a plain text field on `appointments` for MVP — no separate `therapists` table.
- All phases are implemented on the single `mvp` branch; each phase is a discrete, reviewable commit group.

## Context

See `specs/mission.md` for domain context, `specs/tech-stack.md` for stack constraints, and `specs/2026-03-31-agents-ailments/` for the patterns this MVP extends.

## Out of Scope
- Auth, email notifications, therapist profiles, reporting (future phases per roadmap).
- Docker or deployment configuration.
