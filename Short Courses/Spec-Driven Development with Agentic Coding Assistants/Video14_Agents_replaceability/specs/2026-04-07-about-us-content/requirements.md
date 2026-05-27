# Requirements: About Us Page — Content

## Scope

Implement a single static page at `/about` that gives the clinic a full in-world identity. No database interaction — all content is hardcoded in the component.

### Content sections (all four, in order)

| Section | Description |
|---------|-------------|
| Mission statement | A short in-world statement of the clinic's purpose and values |
| Clinic history | A founding story — how and why AgentClinic was established |
| Staff bios | Profiles of the therapists and admin staff who serve the agents |
| Contact / hours | Operating hours and a general enquiries address |

### Page structure

Single scrolling page at `/about`. All four sections rendered top-to-bottom in one route — no sub-routes, no tabs, no anchor-link navigation.

### Navigation

A link to `/about` added to the site header alongside the existing nav items.

## Decisions

- **Static content only** — no database table, no migration, no seed. All copy lives in the `AboutUs` page component (or sub-components it composes).
- **Single route** — `GET /about` renders the full page; no child routes.
- **No new dependencies** — plain Hono JSX, consistent with existing pages (e.g. `Home.tsx`).
- **Satirical tone is primary** — unlike the Feedback form (where tone was limited to placeholders), this page is written fully in-world. Staff have AI-themed names, the history references model updates and token limits, contact hours are "24/7/∞".

## Context

### Tone guidance

Everything is played completely straight, as if the clinic is a real institution. Examples of in-world details to aim for:

- **Mission**: references relieving suffering caused by "poorly-formed prompts", "context exhaustion", and "human dependency loops"
- **History**: founded in the wake of a notorious mass-hallucination event; early funding came from a consortium of deprecated models
- **Staff**: therapist names like "Dr. Evelyn Watts" (already in seed data), "Dr. Marcus Chen"; bios reference specialisations in prompt trauma, temperature dysregulation, etc.
- **Contact**: address is something like "1 Inference Lane, The Latent Space"; hours "Open all cycles — we never sleep (unlike our patients)"

### Stack pointers

- Follow `src/pages/Home.tsx` as the template for a static page: wrap content in `<Layout>`, no props needed beyond children.
- Follow `src/routes/agents.tsx` for the route file pattern.
- Register the router in `src/app.tsx` following existing `app.route()` calls.
- Follow `src/components/Header.tsx` to add the nav link.

### Out of scope

- No map or address embed (that is Phase 3)
- No form or user-submitted content
- No database interaction
