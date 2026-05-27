# Validation: About Us Page — Content

Implementation is complete and ready to merge when all of the following pass.

## Automated Tests

- [ ] `npm test` exits 0 with no failures
- [ ] `npm run typecheck` exits 0 with no type errors

### Specific test coverage required

- [ ] `GET /about` responds with HTTP 200
- [ ] Response HTML contains an `<h1>` heading
- [ ] Response HTML contains mission-related content
- [ ] Response HTML contains at least one staff name (e.g. "Dr. Evelyn Watts")
- [ ] Response HTML contains contact or hours information
- [ ] `AboutUs` component renders all four content sections
- [ ] `AboutUs` component renders within `<Layout>` (contains `<header` and `<footer`)

## Manual Checks

- [ ] Visiting `/about` renders a full page with header and footer
- [ ] All four sections are visible when scrolling: Mission, History, Staff, Contact & Hours
- [ ] The "About" nav link appears in the header and routes correctly
- [ ] Staff bios read as coherent in-world profiles (not placeholder text)
- [ ] Clinic history references AI-specific events or concepts (not generic filler)
- [ ] Contact section includes address and hours in in-world language

## Tone Check

- [ ] All four sections are written fully in-world — no "Lorem ipsum" or placeholder copy
- [ ] Staff names and specialisations are AI-themed and consistent with existing seed data names
- [ ] Tone is played straight throughout — no winking at the reader

## Definition of Done

All automated tests pass, all manual checks confirmed, no leftover TODOs or placeholder text in the component, and the branch is rebased cleanly onto `main`.
