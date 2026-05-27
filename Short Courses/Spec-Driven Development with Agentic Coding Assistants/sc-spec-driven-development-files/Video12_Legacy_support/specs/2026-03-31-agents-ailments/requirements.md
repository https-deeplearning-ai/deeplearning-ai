# Requirements — Phase 2: Agents & Ailments

## Scope

Phase 2 delivers the first real content of AgentClinic: a shared layout system, a SQLite database with seed data, and the first two domain entities — agents and ailments.

## Decisions

### Layout
- A server-side JSX layout component wraps every route: header, nav, main, footer.
- CSS uses **PicoCSS** (classless variant) for base styling — loaded via CDN or npm package, no build step required.
- A minimal `styles.css` supplements Pico with any project-specific overrides (custom properties for brand tokens if needed).
- Mobile-first responsive layout is provided by Pico out of the box.

### Database
- SQLite via `better-sqlite3`.
- Migrations are plain `.sql` files (e.g., `001_create_agents.sql`) in a `migrations/` directory.
- A TypeScript bootstrap function reads and executes migration files in filename order at server startup.
- No ORM; queries are written directly in TypeScript using `better-sqlite3`.

### Seed Data
- Seed scripts populate `agents` and `ailments` tables with fictional but coherent entries.
- Seeds run after migrations, are idempotent (safe to run more than once), and live in a `seeds/` directory or alongside migrations.

### Routes
- `GET /agents` — list all agents (name, model type, status).
- `GET /agents/:id` — single agent profile: name, model type, current status, presenting complaints (linked ailments).
- `GET /ailments` — list all ailments.
- Agents and ailments are linked via a join table (`agent_ailments`).

## Context

This phase establishes patterns that every later phase builds on:
- The layout component is the base for all future pages.
- The migration + seed pattern is reused in Phases 3, 4, and 5.
- The agent detail page is the anchor for appointment booking in Phase 4.

See `specs/mission.md` for domain context and `specs/tech-stack.md` for stack constraints.

## Out of Scope
- Therapies, appointments, and the staff dashboard (later phases).
- Auth, email, or any external integrations.
- Error pages and input sanitization (Phase 7).
