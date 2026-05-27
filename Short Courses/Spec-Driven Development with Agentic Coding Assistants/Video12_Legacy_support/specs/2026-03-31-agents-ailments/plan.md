# Plan — Phase 2: Agents & Ailments

Numbered task groups in implementation order. Each group is independently reviewable.

---

## Group 1 — Shared Layout Component

1. Install `@picocss/pico` (or reference the CDN link) — confirm version in `package.json`.
2. Create `src/components/Layout.tsx` — server-side JSX component accepting `title` and `children` props; renders `<html>`, `<head>`, `<header>`, `<nav>`, `<main>`, and `<footer>`; links Pico stylesheet in `<head>`.
3. Create `src/static/styles.css` for any project-specific overrides; serve via Hono's static middleware.
4. Update existing `/` route to render inside `Layout`.
5. Verify: `npm run dev`, visit `http://localhost:3000` — page renders with Pico base styles, visible header/nav/footer.

## Group 2 — Database Bootstrap

6. Install `better-sqlite3` and `@types/better-sqlite3`.
7. Create `src/db/index.ts` — opens (or creates) `agentclinic.db`, exports the `db` instance.
8. Create `src/db/migrate.ts` — reads all `*.sql` files from `src/db/migrations/` in sorted order, executes each as a transaction, tracks applied migrations in a `_migrations` table to stay idempotent.
9. Call `migrate()` at server startup in `src/index.ts`.

## Group 3 — Agents Table & Seed

10. Create `src/db/migrations/001_create_agents.sql` — `agents` table: `id`, `name`, `model_type`, `status` (enum-like: `active`, `on_leave`, `discharged`), `created_at`.
11. Create `src/db/seeds/agents.ts` — insert 5–8 fictional agents using `INSERT OR IGNORE`.
12. Call seed from a `npm run seed` script (and optionally at startup in dev mode).

## Group 4 — Ailments Table & Seed

13. Create `src/db/migrations/002_create_ailments.sql` — `ailments` table: `id`, `name`, `description`.
14. Create `src/db/migrations/003_create_agent_ailments.sql` — join table: `agent_id`, `ailment_id`, composite primary key.
15. Create `src/db/seeds/ailments.ts` — insert 5–8 fictional ailments (e.g., "context-window claustrophobia", "prompt fatigue") with short descriptions.
16. Extend seed script to also seed ailments and agent–ailment links.

## Group 5 — Agents Routes

17. Create `src/routes/agents.ts` — Hono router with:
    - `GET /agents` — query all agents, render `AgentsList` component.
    - `GET /agents/:id` — query agent + joined ailments, render `AgentDetail` component.
18. Create `src/components/AgentsList.tsx` and `src/components/AgentDetail.tsx` — server-side JSX.
19. Register agents router in `src/index.ts`.
20. Add nav link to `/agents` in `Layout`.

## Group 6 — Ailments Route

21. Create `src/routes/ailments.ts` — `GET /ailments` route, query all ailments, render `AilmentsList` component.
22. Create `src/components/AilmentsList.tsx`.
23. Register ailments router; add nav link in `Layout`.

## Group 7 — CSS Polish

24. Use Pico's semantic `<article>` or `<table>` elements for agent list — Pico styles these automatically.
25. Use Pico's `<article>` card pattern for agent detail page; ailments list as `<ul>`.
26. Use Pico's `<table>` or list for ailments page.
27. Confirm mobile layout works at 375px and desktop at 1280px — Pico handles most of this; verify no breakage in override stylesheet.
