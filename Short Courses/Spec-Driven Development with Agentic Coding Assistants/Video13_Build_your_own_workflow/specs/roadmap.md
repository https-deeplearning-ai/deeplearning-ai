# Roadmap

Phases are intentionally small — each should be implementable in one focused session.

---

## Phase 1: Feedback Form (Complete)

**Goal:** Let visitors submit feedback about the clinic.

- [x] Add `feedback` table to the database schema (migration)
- [x] Seed a few example feedback entries
- [x] Build `FeedbackForm` component (name, message fields)
- [x] Add POST route to handle form submission and persist to DB
- [x] Add `FeedbackList` component to display submitted feedback
- [x] Wire up a `/feedback` page with form + list
- [x] Link `/feedback` from the site navigation

---

## Phase 2: About Us Page — Content

**Goal:** Give the clinic a real identity with static content.

- [ ] Create an `AboutUs` page component
- [ ] Write satirical clinic history, staff bios, and "founding story"
- [ ] Add `/about` route
- [ ] Link `/about` from navigation

---

## Phase 3: About Us Page — Map

**Goal:** Show the clinic's location on a map.

- [ ] Decide on map embed approach (static image vs. iframe vs. API)
- [ ] Add address display to the About Us page
- [ ] Embed map on the page
- [ ] Ensure it degrades gracefully without JavaScript

---

## Phase 4: Customer Reviews — Display

**Goal:** Show patient testimonials on the site.

- [ ] Add `reviews` table to schema (migration)
- [ ] Seed a handful of satirical patient reviews
- [ ] Build `ReviewsList` component
- [ ] Add `/reviews` page

---

## Phase 5: Customer Reviews — Submission

**Goal:** Let agents (and curious humans) submit reviews.

- [ ] Build `ReviewForm` component (agent name, rating, comment)
- [ ] Add POST route to persist new reviews
- [ ] Display submitted reviews on `/reviews`
- [ ] Basic validation (required fields, rating range)
