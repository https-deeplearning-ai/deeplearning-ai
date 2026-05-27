# Plan — MVP (Phases 3–7)

Numbered task groups in implementation order. Each group is independently reviewable and maps to one roadmap phase.

---

## Phase 3 — Therapies Catalog

### Group 1 — Therapies Table & Seed
1. Create `src/db/migrations/004_create_therapies.sql` — `therapies` table: `id`, `name`, `description`.
2. Create `src/db/migrations/005_create_ailment_therapies.sql` — join table: `ailment_id`, `therapist_id`, composite primary key.
3. Create `src/db/seeds/therapies.ts` — insert 5–8 fictional therapies (e.g., "Prompt Detox", "Context Compression Therapy") using `INSERT OR IGNORE`.
4. Extend seed runner to include therapies and ailment–therapy links.

### Group 2 — Therapies Route & Component
5. Create `src/routes/therapies.ts` — `GET /therapies` route, query all therapies, render `TherapiesList` component.
6. Create `src/components/TherapiesList.tsx` — server-side JSX list of therapies with name and description.
7. Register therapies router in `src/index.ts`; add `/therapies` nav link in `Layout`.
8. Update ailment detail or list to surface recommended therapies for each ailment.

---

## Phase 4 — Appointment Booking

### Group 3 — Appointments Table
9. Create `src/db/migrations/006_create_appointments.sql` — `appointments` table: `id`, `agent_id` (FK), `therapist` (text), `datetime` (text/ISO8601), `status` (default `pending`), `created_at`.

### Group 4 — Booking Form & Confirmation
10. Create `src/routes/appointments.ts` — Hono router with:
    - `GET /appointments/new?agentId=:id` — render booking form pre-filled with agent.
    - `POST /appointments` — validate inputs, insert row, redirect to confirmation.
    - `GET /appointments/:id/confirmation` — render confirmation page.
11. Create `src/components/AppointmentForm.tsx` and `src/components/AppointmentConfirmation.tsx`.
12. Add "Book Appointment" link/button to `AgentDetail` component.
13. Register appointments router in `src/index.ts`.

### Group 5 — Server-side Validation
14. Validate required fields (`agentId`, `therapist`, `datetime`) and return form with error messages on failure.
15. Sanitize `therapist` and `datetime` inputs (strip HTML, trim whitespace).

---

## Phase 5 — Staff Dashboard

### Group 6 — Dashboard Route & Component
16. Create `src/routes/dashboard.ts` — `GET /dashboard`:
    - Query count of agents, open appointments (`status = 'pending'`), and distinct ailments linked to active agents.
    - Render `Dashboard` component with summary cards and table views.
17. Create `src/components/Dashboard.tsx` — summary count cards + tables for recent agents and open appointments.
18. Register dashboard router; add `/dashboard` nav link in `Layout`.

---

## Phase 6 — Polish & Accessibility

### Group 7 — Responsive Layout Audit
19. Review every page added in Phases 3–5 at 375px and 1280px viewports.
20. Ensure no horizontal scroll at 375px; content stacks sensibly.

### Group 8 — Semantic HTML & Keyboard Navigation
21. Audit all new pages for proper landmark roles (`<header>`, `<nav>`, `<main>`, `<footer>`), heading hierarchy, and list markup.
22. Add visible `:focus` styles to all interactive elements (links, buttons, form inputs) in `styles.css`.
23. Verify tab order is logical on the booking form.

---

## Phase 7 — Hardening

### Group 9 — Error Pages
24. Create a 404 handler in `src/index.ts` (Hono `app.notFound`) — render a styled `NotFound` JSX component.
25. Create a 500 handler (`app.onError`) — render a styled `ServerError` JSX component; log the error.

### Group 10 — Logging Middleware
26. Create `src/middleware/logger.ts` — Hono middleware that logs method, path, status code, and response time to stdout.
27. Register logger middleware before all routes in `src/index.ts`.
