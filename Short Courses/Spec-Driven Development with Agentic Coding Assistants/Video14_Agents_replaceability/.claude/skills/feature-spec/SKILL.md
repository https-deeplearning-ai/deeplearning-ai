---
name: feature-spec
description: Kicks off a new AgentClinic feature by finding the next incomplete phase in specs/roadmap.md, creating a git branch, interviewing the user about scope/decisions/context, and writing a dated spec directory under specs/ containing plan.md, requirements.md, and validation.md. Trigger when the user says "feature spec", "next phase", "start the next feature", or invokes /feature-spec.
---

# Feature Spec

## Workflow

### 1. Find the next phase

Read `specs/roadmap.md`. The next phase is the first section whose items are all `[ ]`. Note its name to derive the branch and directory name.

### 2. Create the branch

```
git checkout -b phase-N-<kebab-name>
```

### 3. Interview the user — BEFORE writing any files

Use `AskUserQuestion` with exactly **3 questions in one call**:

| Header | Question focus |
|--------|---------------|
| **Scope** | What the feature collects, exposes, or does — fields, page behaviour, data shape |
| **Decisions** | Key implementation choices — storage, visibility, validation, UX pattern |
| **Context** | Tone, constraints, or anything shaping the spec — satirical copy level, stack limits, open questions |

Do **not** write any files until the user has answered all three questions.

### 4. Read guidance files

Read `specs/mission.md` and `specs/tech-stack.md` before drafting.

### 5. Create the spec directory

Name: `specs/YYYY-MM-DD-<feature-name>/` using today's date.

#### `requirements.md`
- Scope section: what is and is not included; field/data table if applicable
- Decisions section: choices made and why (draw from user answers)
- Context section: tone rules, stack pointers, existing patterns to follow

#### `plan.md`
- Numbered task groups: Database → Components → Page & Route → Navigation → Tests
- Each group has numbered sub-tasks; groups should be independently implementable

#### `validation.md`
- Automated: `npm test` and `npm run typecheck` pass; specific assertions required
- Manual: browser walkthrough, form behaviour, edge cases
- Tone check if the feature has user-facing copy
- Definition of done

## Stack constraints

- Hono 4.x + Hono JSX (SSR) + SQLite via `better-sqlite3` + Vitest — no new dependencies without user approval
- POST forms use POST/redirect/GET
- No client-side JS
- Migrations in `src/db/migrations/` as numbered `.sql` files
- Satirical tone in label/placeholder copy only, not in structure or logic
