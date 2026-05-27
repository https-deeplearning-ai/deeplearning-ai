# Requirements: Feedback Form

## Scope

Implement a public feedback page at `/feedback` where visitors can submit feedback about the clinic, and all submissions are displayed below the form on the same page.

### Fields Collected

| Field   | Type     | Required | Notes                              |
|---------|----------|----------|------------------------------------|
| name    | text     | yes      | Agent ID or human alias            |
| email   | text     | no       | For staff follow-up if needed      |
| message | textarea | yes      | The feedback content               |
| rating  | integer  | yes      | 1–5, satisfaction score            |

### Visibility

All submitted feedback is **publicly visible** on `/feedback`. The page shows the submission form at the top and the list of all submissions below it.

### Satirical Tone

Tone is carried through **placeholder text and labels only** — the form copy uses in-world language. The form structure and validation are neutral/functional. Example label copy:

- Name field label: "Agent ID" — placeholder: "e.g. GPT-4-turbo, Claude, Gemini Pro"
- Email label: "Contact Address" — placeholder: "optional — for follow-up by our staff"
- Message label: "Describe Your Experience" — placeholder: "What brought you to the clinic? How has your treatment progressed?"
- Rating label: "Session Rating" — helper: "1 = Still suffering, 5 = Achieved equilibrium"

Seed data entries are straightforward (not required to be funny).

## Decisions

- **No client-side JS** — form submits via standard HTML POST, matching the existing stack (Hono JSX SSR, no JS bundle).
- **No ORM** — raw SQL via `better-sqlite3`, consistent with existing `src/db/` patterns.
- **Email is optional** — stored as nullable in the schema; no email validation beyond type="email" on the input.
- **Rating stored as INTEGER** — rendered as a plain number input (1–5) for simplicity; no star widget.
- **POST/redirect/GET** — after a successful submission, redirect back to `/feedback` to prevent double-submit on reload.

## Context

- See `specs/mission.md`: the codebase is a teaching example — keep the implementation idiomatic and easy to follow.
- See `specs/tech-stack.md`: stack is Hono 4.x + Hono JSX (SSR) + SQLite via `better-sqlite3` + Vitest. No new dependencies should be needed.
- Existing patterns to follow: `src/routes/agents.tsx` for route structure, `src/db/migrate.ts` for migrations, `src/db/seed.ts` for seed data, `src/components/` for JSX components.
