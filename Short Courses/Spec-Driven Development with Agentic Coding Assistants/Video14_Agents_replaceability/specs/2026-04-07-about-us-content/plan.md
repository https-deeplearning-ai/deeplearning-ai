# Plan: About Us Page — Content

No database work required for this phase — all content is static.

---

## Group 1: Page Component

1. Create `src/pages/AboutUs.tsx`:
   - Wraps content in `<Layout>`
   - Four sections rendered in order: Mission, History, Staff, Contact & Hours
   - All copy written fully in-world (see requirements for tone guidance)
   - Staff bios should reference Dr. Evelyn Watts and Dr. Marcus Chen (names already in seed data)

---

## Group 2: Route

2. Create `src/routes/about.tsx`:
   - `GET /` renders `<AboutUs />`
   - No database argument needed — export `aboutRouter()` with no parameters

3. Register in `src/app.tsx`:
   - Import `aboutRouter` and add `app.route("/about", aboutRouter())`

---

## Group 3: Navigation

4. Add an "About" link to `src/components/Header.tsx`:
   - `<a href="/about">About</a>` as a new `<li>` in the nav list

---

## Group 4: Tests

5. Add to `tests/app.test.tsx` — `describe("GET /about")`:
   - Returns 200
   - Contains `<h1>` with "About" or clinic name
   - Contains the word "mission" (case-insensitive) somewhere on the page
   - Contains at least one staff name (e.g. "Dr. Evelyn Watts")
   - Contains contact or hours information

6. Add to `tests/components.test.tsx` — `describe("AboutUs")`:
   - Renders all four sections (mission, history, staff, contact)
   - Renders inside a `<Layout>` (contains `<header` and `<footer`)
