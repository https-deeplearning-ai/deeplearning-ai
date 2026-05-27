# Vercel Database Options with Good Local DX

**Context:** Relational SQL, willing to use a compatible local alternative (not strict parity required), Vercel-native services are acceptable.

## Top Choices

### 1. Neon (Recommended)
Vercel's first-party Postgres integration. Serverless Postgres with branching, instant cold starts, and a generous free tier.

- **Prod:** Neon (Postgres-compatible, deployed via Vercel integration)
- **Local:** `docker run postgres` or `brew install postgresql` — same SQL dialect, same ORM
- **DX:** Vercel dashboard integration, connection strings auto-injected via env vars
- **Caveat:** Serverless connection pooling requires `@neondatabase/serverless` or a pooler like PgBouncer for high-concurrency

### 2. Vercel Postgres (powered by Neon)
Same as Neon but provisioned directly from the Vercel dashboard with zero config.

- **Local:** Standard Postgres locally; swap the `DATABASE_URL` env var
- **Best for:** Teams that want everything in one dashboard

### 3. Turso (libSQL / SQLite-compatible)
Edge-native SQLite with HTTP replication. Great if "close enough" means SQLite locally.

- **Prod:** Turso hosted libSQL
- **Local:** SQLite file — same engine, exact parity, zero infra
- **DX:** `turso dev` spins up a local replica; Drizzle ORM has first-class support
- **Caveat:** Not standard Postgres — limited ecosystem compared to PG

### 4. Supabase
Hosted Postgres with extras (auth, storage, realtime).

- **Prod:** Supabase cloud
- **Local:** `supabase start` runs a full local stack via Docker
- **Caveat:** Heavier local setup; overkill if you don't need the extras

## ORM Recommendation

For any of the Postgres options, **Drizzle ORM** or **Prisma** both work well with Vercel + local Postgres. Drizzle is lighter and has excellent Turso/libSQL support too.

## Recommendation

Start with **Vercel Postgres (Neon)** — provision it from the dashboard, use a local Postgres via Docker for dev, and connect with Drizzle or Prisma. Zero friction, standard SQL, easy to migrate later.
