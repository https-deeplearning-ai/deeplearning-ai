# Validation — MVP (Phases 3–7)

The MVP is complete and ready to merge when all three criteria below pass for every phase.

---

## 1. TypeScript Compiles Clean

```
npx tsc --noEmit
```

Must exit with code 0 and no errors or warnings.

---

## 2. Vitest Unit Tests

Run with:

```
npm test
```

All tests must pass. Required coverage by phase:

### Phase 3 — Therapies
- `therapies` table exists with expected columns after migration.
- `ailment_therapies` join table exists after migration.
- After seeding, `SELECT COUNT(*) FROM therapies` returns ≥ 5.
- At least one `ailment_therapies` row exists after seeding.
- Running seed twice does not duplicate rows.
- `GET /therapies` returns HTTP 200 and lists therapy names.

### Phase 4 — Appointments
- `appointments` table exists with expected columns after migration.
- `POST /appointments` with valid data returns HTTP 302 redirect to confirmation.
- `POST /appointments` with missing required fields returns HTTP 400 with error message in body.
- `GET /appointments/:id/confirmation` for a known appointment returns HTTP 200.
- `GET /agents/:id` for a seeded agent includes a "Book Appointment" link.

### Phase 5 — Dashboard
- `GET /dashboard` returns HTTP 200.
- Response body includes summary counts (agents, open appointments, ailments).

### Phase 6 — Accessibility (automated)
- All new route responses include `<main>`, `<header>`, and `<footer>` landmarks.
- All new route responses include a `<h1>` element.

### Phase 7 — Hardening
- `GET /nonexistent-route` returns HTTP 404 and HTML (not a stack trace).
- Request logger middleware emits a line to stdout for each request (spy on `console.log` or similar).

---

## 3. Manual Smoke Test Checklist

Start the dev server (`npm run dev`) and verify each item visually in a browser.

### Phase 3 — Therapies
- [ ] `/therapies` lists at least 5 therapies with names and descriptions.
- [ ] Nav contains a working link to `/therapies`.
- [ ] Ailment detail or list page shows recommended therapies.

### Phase 4 — Appointment Booking
- [ ] Agent detail page (`/agents/:id`) has a "Book Appointment" link/button.
- [ ] Booking form pre-fills the agent name/ID.
- [ ] Submitting the form with all valid fields redirects to a confirmation page.
- [ ] Confirmation page displays the booked agent, therapist, and datetime.
- [ ] Submitting with missing fields re-renders the form with visible error messages.

### Phase 5 — Dashboard
- [ ] `/dashboard` loads without error.
- [ ] Summary counts for agents, open appointments, and ailments are visible.
- [ ] Tables or lists for recent agents and open appointments are rendered.
- [ ] Nav contains a working link to `/dashboard`.

### Phase 6 — Polish & Accessibility
- [ ] At 375px viewport, all pages (Phases 3–5) stack vertically with no horizontal scroll.
- [ ] All interactive elements have a visible focus ring when navigated by keyboard (Tab key).
- [ ] Booking form is fully operable without a mouse (Tab, Enter, Shift+Tab).
- [ ] Each page has a single `<h1>` and a logical heading hierarchy.

### Phase 7 — Hardening
- [ ] Visiting a nonexistent URL (e.g., `/does-not-exist`) renders a styled 404 page, not a raw error.
- [ ] Dev server console shows one log line per request with method, path, status, and timing.
- [ ] Submitting the booking form with `<script>` tags in text fields does not render script tags in the confirmation page.
