# Tech Stack

## Language & Runtime

- **TypeScript 5.5** — strict mode, compiled with `tsc`
- **Node.js** — runtime via `@hono/node-server`
- **tsx** — TypeScript execution for development watch mode (`tsx watch`)

## Backend / API Layer

- **Hono 4.x** — lightweight, fast web framework
  - Routes defined in `src/routes/` (agents, ailments, therapies, appointments, dashboard)
  - Middleware in `src/middleware/` (logger)
  - No REST/GraphQL/tRPC abstraction — Hono routing is the API layer

## Frontend

- **Hono JSX** — server-side rendering via `.tsx` components; no client-side framework
  - Components live in `src/components/`
  - Pages live in `src/pages/`
  - No hydration, no JavaScript bundle sent to the browser
- **Vanilla CSS** — single stylesheet at `static/style.css`

## Database / Persistence

- **SQLite** — via `better-sqlite3` (synchronous, embedded)
  - Database file: `agentclinic.db`
  - Schema managed by `src/db/migrate.ts` (hand-written migrations, no ORM)
  - Seed data via `src/db/seed.ts` / `npm run seed`
  - Types defined in `src/db/types.ts`

## Testing

- **Vitest 4.x** — test runner
  - `tests/app.test.tsx` — route/integration tests
  - `tests/components.test.tsx` — component rendering tests
  - `tests/db.test.ts` — database layer tests
  - Run with `npm test` (`vitest run --passWithNoTests`)

## Tooling

- **TypeScript compiler** — `npm run build` (compile), `npm run typecheck` (check only)
- **tsx** — `npm run dev` (watch mode, no compile step needed)
- No linter or formatter currently configured

## Gaps / Future Considerations

- No linter (ESLint) or formatter (Prettier) — worth adding for a teaching codebase
- No ORM — direct SQL is intentional for clarity, but could introduce Drizzle/Kysely later
- No CI pipeline defined
- No client-side interactivity layer — if forms need progressive enhancement, consider HTMX
