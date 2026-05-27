# Validation: Feedback Form

Implementation is complete and ready to merge when all of the following pass.

## Automated Tests

- [ ] `npm test` exits 0 with no failures
- [ ] `npm run typecheck` exits 0 with no type errors

### Specific test coverage required

- [ ] `getAllFeedback()` returns seeded rows after migration + seed
- [ ] `createFeedback()` persists a row and returns it with an `id` and `created_at`
- [ ] `GET /feedback` responds with HTTP 200
- [ ] `POST /feedback` with valid body redirects (HTTP 3xx) to `/feedback`
- [ ] `POST /feedback` with missing `name` or `message` does not create a row
- [ ] `FeedbackForm` renders inputs for name, email, message, and rating
- [ ] `FeedbackList` renders a list when given items
- [ ] `FeedbackList` renders the empty-state message when given an empty array

## Manual Checks

- [ ] Visiting `/feedback` shows the form and any existing submissions
- [ ] Submitting the form with all fields populated adds an entry that appears on page reload
- [ ] Submitting without the required fields (name, message, rating) is prevented (HTML5 or server-side)
- [ ] Email field is optional — form submits successfully without it
- [ ] Rating accepts only 1–5; values outside that range are rejected
- [ ] Reloading the page after submit does not re-submit (POST/redirect/GET pattern)
- [ ] A "Feedback" link appears in the site navigation and routes correctly

## Tone Check

- [ ] Form labels and placeholders use in-world language ("Agent ID", "Session Rating", etc.)
- [ ] No jokes or satirical copy in the form structure itself — comedy is in the copy only

## Definition of Done

All automated tests pass, all manual checks are confirmed, and the branch is rebased cleanly onto `main` with no leftover debug code or `console.log` statements.
