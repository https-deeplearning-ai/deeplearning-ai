# Validation — Phase 2: Agents & Ailments

Phase 2 is complete and ready to merge when all three criteria below pass.

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

All tests must pass. Required test coverage:

### Database / Migrations
- `migrate()` runs without error against an in-memory or temp SQLite file.
- Running `migrate()` twice is idempotent (no duplicate-migration errors).
- `agents` table exists with the expected columns after migration.
- `ailments` table exists with the expected columns after migration.
- `agent_ailments` join table exists after migration.

### Seed Data
- After seeding, `SELECT COUNT(*) FROM agents` returns ≥ 5.
- After seeding, `SELECT COUNT(*) FROM ailments` returns ≥ 5.
- After seeding, at least one `agent_ailments` row exists.
- Running seed twice does not duplicate rows.

### Routes
- `GET /` returns HTTP 200 and HTML containing layout landmarks (`<header>`, `<main>`, `<footer>`).
- `GET /agents` returns HTTP 200 and lists agent names in the response body.
- `GET /agents/:id` for a known seed agent returns HTTP 200 and includes the agent's name and at least one ailment.
- `GET /agents/999` (non-existent) returns HTTP 404.
- `GET /ailments` returns HTTP 200 and lists ailment names.

---

## 3. Manual Smoke Test Checklist

Start the dev server (`npm run dev`) and verify each item visually in a browser.

### Layout
- [ ] Header, nav, main, and footer are visible on every page.
- [ ] Nav contains working links to `/`, `/agents`, and `/ailments`.
- [ ] Stylesheet loads (no unstyled text dump).
- [ ] At 375px viewport width, layout stacks vertically with no horizontal scroll.
- [ ] At 1280px viewport width, layout uses available space sensibly.

### Agents
- [ ] `/agents` lists at least 5 agents with name, model type, and status.
- [ ] Clicking an agent navigates to `/agents/:id`.
- [ ] Agent detail page shows name, model type, status, and presenting ailments.
- [ ] Visiting `/agents/99999` renders a 404-style response (even if plain text for now).

### Ailments
- [ ] `/ailments` lists at least 5 ailments with names and descriptions.

### Static Asset
- [ ] PicoCSS styles are applied — body text is styled, not a browser-default serif dump.
- [ ] Browser DevTools Network tab shows PicoCSS loaded (CDN or served file) with HTTP 200.
- [ ] Override `styles.css` loads with HTTP 200 (not inline).
