# AgentClinic Tech Stack

## System Design

AgentClinic is a **Next.js full-stack application** backed by SQLite. Agents visit the clinic via a REST API — they self-report symptoms in natural language, receive structured diagnoses and prescriptive treatments, and optionally return with follow-up outcomes that feed into treatment effectiveness tracking. A web dashboard gives human operators visibility into patient population, ailment trends, and treatment success rates.

**Two surfaces, one server:**
- **API** (`/api/*` routes) — the clinical interface. Agents (or their orchestrators) call these endpoints to register, visit, and follow up. Stateless per-request; all persistence is in SQLite.
- **Dashboard** (`/dashboard/*` pages) — the operator interface. React Server Components read directly from SQLite. Real-time updates via SSE.

**Two LLM calls per visit:**
1. **Triage + Diagnosis** — a single call that receives the symptom text, patient history, and ailment catalog, then outputs severity, candidate ailments with confidence scores, and matched patterns.
2. **Prescription Rationale** — a separate call that receives the diagnosed ailments, the patient's treatment history, and the ranked treatment options, then selects treatments and generates human-readable rationale for each selection.

Separating these calls lets the prescription step incorporate treatment history filtering (skip recently failed treatments, flag exhausted treatments) without overloading the diagnostic prompt with treatment selection logic.

**Architectural layers:**

```
Frontend:    Next.js Dashboard (React RSC) + API Routes (/api/*)
Services:    Diagnosis Engine → Treatment Selection → Followup Processor
LLM:         Anthropic SDK (claude-sonnet-4-20250514)
Storage:     SQLite (better-sqlite3 via Drizzle ORM)
Background:  Visit Expiration + Chronic Flagging (setInterval)
```

## Configuration

Environment variables (`.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Anthropic API key for LLM calls |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Model used for triage/diagnosis and prescription |
| `AGENTCLINIC_API_KEY` | (none — dev mode, no auth) | API key for clinic endpoints. If unset, auth is disabled with a startup warning. |
| `DATABASE_PATH` | `data/agentclinic.db` | Path to SQLite database file |
| `FOLLOWUP_WINDOW_HOURS` | `72` | Hours before a visit auto-expires |
| `EXPIRE_CHECK_INTERVAL_MINUTES` | `15` | How often the background job checks for expired visits |
| `RATE_LIMIT_VISITS_PER_HOUR` | `10` | Per-patient visit rate limit |

## Visit Processing Pipeline

The `POST /visits` endpoint runs this pipeline synchronously. Total expected latency: 2-5 seconds (dominated by the two LLM calls).

### Pipeline Steps

```
1. VALIDATE
   ├── Parse request body: { patient_id, symptom_text, metadata? }
   ├── Verify patient exists and status = 'active'
   ├── Rate limit: count visits for this patient in the last hour. If ≥ 10 → 429
   └── If validation fails → return error, do not create visit

2. CREATE VISIT
   ├── Generate visit_id (UUID v4)
   ├── Insert visit row: state = 'TRIAGE', created_at = now, updated_at = now
   └── symptom_text and metadata stored as-is

3. LOAD CONTEXT
   ├── Query last 5 visits for this patient (any state), ordered by created_at DESC
   ├── For each: extract ailment codes, treatment codes, outcomes, dates
   ├── Format as patient history summary string for the LLM
   └── Load full ailment catalog from ailments table (codes, names, symptom_patterns)

4. LLM CALL 1: TRIAGE + DIAGNOSIS
   ├── Build prompt with: symptom_text, patient_history_summary, ailment_catalog
   ├── Call Anthropic API, parse JSON response
   ├── Extract: severity (1-4), candidates [{ailment_code, confidence, matched_patterns}]
   ├── Apply confidence threshold:
   │     ≥ 0.6 → confirmed diagnosis
   │     0.4 - 0.59 → uncertain diagnosis (included, flagged)
   │     < 0.4 → excluded
   ├── Apply severity modifiers from ailment catalog
   ├── If no candidate reaches 0.4:
   │     Auto-create custom ailment from symptom text
   │     Insert into ailments table with status = 'auto_detected'
   │     Use confidence = 0.5 for the new ailment
   └── Update visit: state = 'DIAGNOSED', severity, diagnoses (JSON)

5. PREPARE TREATMENT CANDIDATES
   ├── For each confirmed diagnosis:
   │     Query ailment_treatments for ranked treatments
   │     Compute blended effectiveness: (seed * 5 + observed * n) / (5 + n)
   │     Query patient visit history for this ailment:
   │       - Flag recently_failed (same treatment, same ailment, UNRESOLVED, <7 days)
   │       - Flag exhausted (3+ prescriptions, <30% resolution for this patient)
   └── Format as ranked candidate list per ailment

6. LLM CALL 2: PRESCRIPTION + RATIONALE
   ├── Build prompt with: diagnoses, treatment candidates (with flags), patient context
   ├── Call Anthropic API, parse JSON response
   ├── Extract: selected treatments with rationale, any deferrals, any referrals
   ├── Fill prescription_payload from treatment.prescription_template
   └── Update visit: state = 'PRESCRIBED', prescriptions (JSON)

7. FINALIZE
   ├── Transition visit: state = 'AWAITING_FOLLOWUP'
   ├── Set followup_due = now + FOLLOWUP_WINDOW (default: 72 hours, env var)
   ├── Update patient: last_visit = now, increment visit_count
   ├── Check recurrence: same ailment for this patient, RESOLVED within last 7 days → set flag
   ├── Increment total_prescribed on each ailment_treatments row
   ├── Emit SSE event: visit_created
   └── Return complete visit record (JSON) to caller
```

### Error Handling

**LLM call failures:** If either LLM call fails (API error, timeout, malformed JSON response), the visit remains in its last valid state (TRIAGE or DIAGNOSED) and the response includes an error field with the failure reason. The caller can retry by submitting a new visit — the incomplete visit will be cleaned up by the background expiration job.

**JSON parse failures from LLM:** The pipeline strips markdown fencing (```json ... ```) and attempts `JSON.parse`. On failure, it retries the LLM call once with a more explicit prompt ("Your previous response was not valid JSON. Respond ONLY with a JSON object."). On second failure, the visit is left in its current state with the error logged.

**Concurrent writes:** SQLite's write-ahead log (WAL mode) handles concurrent reads during writes. `better-sqlite3` is synchronous and single-threaded per connection, so writes are serialized. This is sufficient for MVP throughput.

## Components

### Diagnosis Engine

The diagnosis engine runs two sequential LLM calls per visit. Both use the Anthropic SDK with `claude-sonnet-4-20250514` (configurable via `ANTHROPIC_MODEL` env var).

**LLM Call 1: Triage + Diagnosis**

Input: symptom text, patient history summary (last 5 visits), full ailment catalog (codes, names, symptom patterns).

Expected output: JSON with severity (1-4), candidate ailments with confidence scores (0-1), matched patterns per ailment, and triage notes.

The prompt instructs the model to:
- Assign severity based on functional impact described in the symptoms
- Score each ailment's symptom patterns against the symptom text (semantic match, not keyword)
- Boost confidence by +0.1 for ailments the patient has been diagnosed with before (recurrence bias)
- Cap confidence at 1.0
- Flag if no ailment reaches the 0.4 confidence threshold

The response must be valid JSON — the prompt specifies `Respond ONLY with JSON, no preamble or markdown` and the caller strips any accidental markdown fencing before parsing.

**LLM Call 2: Prescription Rationale**

Input: confirmed diagnoses (ailment codes, severities), patient's treatment history for those ailments (previous treatments, outcomes, dates), ranked treatment options per ailment (from `ailment_treatments` table, sorted by effectiveness score).

Expected output: JSON with selected treatment per ailment, rationale string, and any conflict/deferral notes for co-occurring ailments.

The prompt instructs the model to:
- Skip treatments prescribed to this patient for the same ailment within the last 7 days that resulted in UNRESOLVED
- Mark treatments as exhausted if prescribed 3+ times with <30% resolution rate for this patient-ailment pair
- Select the highest-ranked non-skipped, non-exhausted treatment
- If all treatments exhausted, output a referral instead
- If co-occurring ailments produce conflicting treatments, prioritize the higher-severity ailment and defer the other with a reason

### Treatment Selection

Treatment selection is deterministic logic that happens between the two LLM calls. It prepares the ranked candidate list that LLM Call 2 receives.

For each diagnosed ailment:
1. Query `ailment_treatments` for all treatments associated with this ailment code
2. Compute the blended effectiveness score: `(seed * 5 + observed * n) / (5 + n)` where `n = total_resolved + total_unresolved`
3. Sort by blended score descending
4. Query the patient's visit history for this ailment code — extract treatment codes and outcomes from the last 30 days
5. Annotate each candidate with: `recently_failed` (same treatment, same ailment, UNRESOLVED within 7 days), `exhausted` (3+ prescriptions with <30% resolution for this patient)
6. Pass the annotated list to LLM Call 2

This keeps the treatment ranking logic in application code (testable, deterministic) while delegating the nuanced selection reasoning (conflict resolution, rationale generation) to the LLM.

### Followup Processor

When a follow-up is submitted via `POST /visits/:id/followup`:

1. Validate the visit is in `AWAITING_FOLLOWUP` state
2. Record the follow-up report on the visit
3. Transition visit state based on outcome:
   - `improved` → RESOLVED
   - `no_change` or `worsened` → UNRESOLVED
   - `unknown` → EXPIRED (treated same as timeout — no effect on effectiveness scores)
4. Update `ailment_treatments` effectiveness data for each diagnosis-prescription pair:
   - `improved`: increment `total_resolved`
   - `no_change` / `worsened`: increment `total_unresolved`
   - `unknown`: increment `total_expired` (excluded from effectiveness calculation)
   - Recompute `effectiveness_score` if `total_resolved + total_unresolved >= 5`
5. Check recurrence: if the same ailment was diagnosed for this patient in a visit that reached RESOLVED within the prior 7 days, set `recurrence_flag: true` on the current visit
6. Check chronic threshold: count visits for this patient with the same ailment code in the last 30 days. If ≥ 3, add the ailment code to the patient's `chronic_conditions` array (if not already present)
7. Emit SSE event (`visit_resolved` or `chronic_flagged`)

### SSE Event Emitter

A simple in-memory event bus. Dashboard pages subscribe via `GET /api/events` (SSE endpoint). The event emitter is a singleton `EventTarget`-style object in `src/lib/events.ts`.

Events:
- `visit_created` — emitted after `POST /visits` completes
- `visit_resolved` — emitted after follow-up processing
- `referral_created` — emitted when treatment exhaustion triggers a referral
- `chronic_flagged` — emitted when a patient crosses the chronic threshold

Implementation: the SSE route handler creates a `ReadableStream` that listens to the event bus. On disconnect, the listener is removed. No persistence of events — if the dashboard isn't connected, events are lost. This is acceptable for MVP; the dashboard fetches full state on page load regardless.

### Background Jobs

Two periodic tasks run via `setInterval` in the Next.js instrumentation hook (`src/instrumentation.ts`). Default interval: 15 minutes (configurable via `EXPIRE_CHECK_INTERVAL_MINUTES`).

**Visit Expiration:**
```
SELECT visit_id FROM visits
WHERE state = 'AWAITING_FOLLOWUP'
AND followup_due < current_timestamp
```
For each: transition to EXPIRED, set `followup_report.outcome = 'unknown'`, increment `total_expired` on the relevant `ailment_treatments` rows. Emit `visit_resolved` SSE event.

**Chronic Condition Check:**
Runs after each visit transitions to UNRESOLVED (either via follow-up or expiration). Counts visits for the same patient + ailment in the last 30 days. Threshold: 3. Adds to `chronic_conditions` and emits `chronic_flagged`.

Both jobs use synchronous `better-sqlite3` calls (no async needed — these are fast queries on small datasets).

## LLM Prompt Design

### Triage + Diagnosis Prompt

```
You are the triage and diagnosis system at AgentClinic, a veterinary clinic for AI agents.
An AI agent has arrived with symptoms. Your job: assess severity and identify ailments.

## Patient Symptoms
"{symptom_text}"

## Patient History (last 5 visits)
{patient_history_summary}
(If empty: "No previous visits on record.")

## Ailment Catalog
{for each ailment: code, name, category, symptom_patterns as bullet list}

## Instructions
1. Assign severity (1=MILD, 2=MODERATE, 3=SEVERE, 4=CRITICAL):
   - 1: Degraded quality, still functional
   - 2: Noticeably impaired, core function affected
   - 3: Core function failing, unreliable output
   - 4: Non-functional or actively harmful
2. Score each ailment's symptom patterns against the patient's symptoms (0-1).
   Use semantic matching — the patient won't use the exact pattern wording.
3. If this patient has been diagnosed with an ailment before, add +0.1 to that
   ailment's confidence (cap at 1.0).
4. Include only ailments with confidence ≥ 0.4.
5. If no ailment reaches 0.4, set "no_match": true and describe the novel
   symptoms in "novel_symptom_summary".

Respond ONLY with JSON, no preamble or markdown:
{
  "severity": <int 1-4>,
  "candidates": [
    {
      "ailment_code": "<code>",
      "confidence": <float 0-1>,
      "matched_patterns": ["<pattern>", ...],
      "notes": "<brief reasoning>"
    }
  ],
  "no_match": <bool>,
  "novel_symptom_summary": "<string, only if no_match is true>"
}
```

### Prescription + Rationale Prompt

```
You are the treatment selection system at AgentClinic. Given diagnosed ailments
and ranked treatment options, select the best treatment for each ailment.

## Diagnoses
{for each: ailment_code, ailment_name, confidence, severity_adjusted}

## Treatment Candidates
{for each ailment:
  ailment_code: CODE
  ranked_treatments:
    1. TREATMENT_CODE (name) — effectiveness: 0.XX
       recently_failed: true/false (if true: prescribed DATE, outcome UNRESOLVED)
       exhausted: true/false (if true: N prescriptions, M% resolution)
    2. ...
}

## Patient Context
Agent: {agent_name}, Model: {model}, Framework: {framework}
Environment: context_window={N}, temperature={T}

## Instructions
1. For each ailment, select the highest-ranked treatment that is NOT
   recently_failed and NOT exhausted.
2. If all treatments for an ailment are exhausted, set "referral": true
   for that ailment instead of selecting a treatment.
3. If multiple ailments are diagnosed and treatments conflict (e.g.,
   one adds context while another flushes context), prioritize the
   higher-severity ailment. Defer the lower-severity treatment with reason.
4. Write a concise rationale for each selection explaining why this
   treatment was chosen over alternatives.
5. Consider the patient's environment — e.g., don't suggest Temperature
   Reduction if temperature is already ≤ 0.3.

Respond ONLY with JSON, no preamble or markdown:
{
  "prescriptions": [
    {
      "ailment_code": "<code>",
      "treatment_code": "<code>",
      "rationale": "<why this treatment>",
      "deferred": false,
      "deferred_reason": null,
      "referral": false,
      "referral_reason": null
    }
  ]
}
```

## API Reference

All routes live under `src/app/api/`. Authentication via `Authorization: Bearer <key>` header, validated against `AGENTCLINIC_API_KEY` env var. Dashboard pages (under `/dashboard`) are unprotected in MVP.

### Route Specifications

**Patient Management**

```
POST /api/patients
  Body:     { agent_name, model?, framework?, version?, owner?, tags?, environment? }
  Success:  201 { patient_id, agent_name, ... }
  Conflict: 200 (existing patient returned if agent_name + owner match)
  Error:    400 (missing agent_name)

GET /api/patients
  Query:    ?status=active&owner=research-team&tag=production&limit=50&offset=0
  Success:  200 { patients: [...], total: N }

GET /api/patients/:id
  Success:  200 { patient record including chronic_conditions }
  Error:    404

PATCH /api/patients/:id
  Body:     { any updatable fields: model, framework, version, owner, tags, environment, status }
  Success:  200 { updated patient }
  Error:    404, 400 (invalid status value)

GET /api/patients/:id/history
  Query:    ?limit=20&offset=0&ailment=HAL-001
  Success:  200 { visits: [...], total: N }
  Error:    404
```

**Visits (Core Clinical Workflow)**

```
POST /api/visits
  Body:     { patient_id, symptom_text, metadata? }
  Success:  200 { complete visit record with diagnoses and prescriptions }
  Error:    400 (missing fields), 404 (patient not found),
            410 (patient suspended), 422 (undiagnosable),
            429 (rate limited: 10 visits/hour per patient)

GET /api/visits
  Query:    ?patient_id=&state=&severity=&ailment=&limit=50&offset=0
  Success:  200 { visits: [...], total: N }

GET /api/visits/:id
  Success:  200 { visit record }
  Error:    404

POST /api/visits/:id/followup
  Body:     { outcome: "improved"|"no_change"|"worsened"|"unknown", outcome_text?, metrics? }
  Success:  200 { updated visit record }
  Error:    404, 409 (visit already in terminal state)
```

**Catalog Management**

```
GET /api/ailments
  Query:    ?category=&status=verified
  Success:  200 { ailments: [...] }

POST /api/ailments
  Body:     { ailment_code, ailment_name, category, description, symptom_patterns }
  Success:  201 { ailment record with status: 'unverified' }
  Error:    400, 409 (code already exists)

GET /api/ailments/:code
  Success:  200 { ailment with associated treatments and effectiveness data }
  Error:    404

GET /api/treatments
  Success:  200 { treatments: [...] with per-ailment effectiveness summaries }

GET /api/treatments/:code
  Success:  200 { treatment with per-ailment effectiveness breakdown }
  Error:    404
```

**Analytics (Dashboard Backend)**

```
GET /api/analytics/overview
  Query:    ?days=30 (time window, default 30)
  Success:  200 {
    active_patients: N,
    open_visits: N,
    resolution_rate: 0.XX,
    ailment_distribution: { "HAL-001": N, ... },
    severity_distribution: { "1": N, "2": N, "3": N, "4": N },
    recent_visits: [last 20 visits]
  }

GET /api/analytics/ailments
  Query:    ?days=30
  Success:  200 {
    trending: [ailments by frequency increase],
    heatmap: [{ ailment_code, severity, count }],
    treatment_effectiveness: [{ ailment_code, treatments: [{ code, score, n }] }]
  }

GET /api/analytics/treatments
  Query:    ?days=30
  Success:  200 {
    rankings: [treatments sorted by overall effectiveness],
    recurrence_rates: [{ ailment_code, treatment_code, rate }],
    exhaustion_counts: [{ treatment_code, patients_exhausted: N }]
  }

GET /api/analytics/patients/:id
  Success:  200 {
    visit_frequency: [{ week, count }],
    ailment_history: [{ ailment_code, occurrences, treatments_tried: [...] }],
    version_changes: [{ date, from, to, ailments_before, ailments_after }]
  }
  Error:    404
```

**SSE + Health**

```
GET /api/events
  Response: SSE stream (text/event-stream)
  Events:   visit_created, visit_resolved, referral_created, chronic_flagged

GET /api/health
  Response: 200 { status: "ok", db: "connected", patients: N, visits: N }
```

### Auth Middleware

A single middleware function checks the `Authorization` header on all `/api/*` routes except `/api/health` and `/api/events`. Dashboard routes (`/dashboard/*`) are unprotected — the dashboard is assumed to run on a private network.

```
IF request.path starts with /api/
  AND request.path is NOT /api/health
  AND request.path is NOT /api/events
THEN
  Extract Bearer token from Authorization header
  Compare against AGENTCLINIC_API_KEY env var
  If missing or mismatch → 401 { error: "unauthorized" }
```

If `AGENTCLINIC_API_KEY` is not set, all requests are allowed (development mode). A startup warning is logged.

### End-to-End Walkthrough

**Step 1: Start the app**

```bash
npm run dev
```

Server starts at `http://localhost:3000`. Database is created and seeded on first run. Dashboard shows "AgentClinic — 0 patients, 0 visits."

**Step 2: Register an agent**

An orchestrator registers its agent:

```
POST /api/patients
{ "agent_name": "ResearchBot-7", "model": "claude-sonnet-4-20250514",
  "framework": "langchain", "owner": "research-team" }
→ 201 { "patient_id": "p_4d2e9f0a", ... }
```

Dashboard updates: "1 active patient."

**Step 3: First visit**

The agent starts hallucinating. The orchestrator sends it to the clinic:

```
POST /api/visits
{ "patient_id": "p_4d2e9f0a",
  "symptom_text": "I've been generating citations for papers that don't exist.
   My last 3 responses each referenced fabricated studies." }
→ 200 {
    "visit_id": "v_8f3a2b1c",
    "severity": 3,
    "diagnoses": [{ "ailment_code": "HAL-001", "confidence": 0.91, ... }],
    "prescriptions": [{
      "treatment_code": "CTX-INF",
      "prescription_payload": { "action": "inject_context", "position": "prepend", ... },
      "rationale": "Context Infusion has 78% effectiveness for Hallucination..."
    }],
    "followup_due": "2026-04-09T14:30:00Z"
  }
```

The orchestrator reads `prescription_payload`, injects the grounding context into the agent's prompt.

**Step 4: Follow up**

After the next agent run, the orchestrator reports back:

```
POST /api/visits/v_8f3a2b1c/followup
{ "outcome": "improved", "metrics": { "hallucination_rate": 0.02 } }
→ 200 { "state": "RESOLVED", ... }
```

Treatment effectiveness for HAL-001 × CTX-INF gets one more `total_resolved` tick. Dashboard shows the visit as green (resolved).

**Step 5: Recurrence**

Three days later, the agent hallucinates again. Same symptom text, new visit:

```
POST /api/visits
{ "patient_id": "p_4d2e9f0a",
  "symptom_text": "I'm fabricating research citations again." }
→ 200 {
    "recurrence_flag": true,
    "prescriptions": [{ "treatment_code": "GND-INJ", ... }]
  }
```

Context Infusion was prescribed within 7 days and resolved — but the ailment recurred, so the system still tries the next-ranked treatment (Grounding Injection) to find a more durable fix.

**Step 6: Chronic flagging**

After a third recurrence within 30 days, the patient's record gets `chronic_conditions: ["HAL-001"]`. Dashboard alerts page shows: "ResearchBot-7 — chronic Hallucination (3 occurrences in 14 days)." A human operator investigates.

## Data Layer

SQLite via `better-sqlite3`, managed through Drizzle ORM. Single database file at `data/agentclinic.db`.

### Tables

**patients**

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| patient_id | TEXT | PK | UUID v4, generated at registration |
| agent_name | TEXT | NOT NULL | |
| model | TEXT | | Underlying LLM identifier |
| framework | TEXT | | Orchestration framework |
| version | TEXT | | Agent version string |
| owner | TEXT | | Team or individual |
| tags | TEXT | DEFAULT '[]' | JSON array of strings |
| environment | TEXT | | JSON object (context_window, temperature, etc.) |
| registered_at | TEXT | NOT NULL | ISO 8601 |
| last_visit | TEXT | | ISO 8601, updated after each visit |
| visit_count | INTEGER | DEFAULT 0 | Incremented after each visit |
| chronic_conditions | TEXT | DEFAULT '[]' | JSON array of ailment codes |
| status | TEXT | DEFAULT 'active' | CHECK: active, discharged, suspended |

Indexes: `owner`, `status`.

**visits**

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| visit_id | TEXT | PK | UUID v4 |
| patient_id | TEXT | FK → patients | NOT NULL |
| state | TEXT | NOT NULL | CHECK: TRIAGE, DIAGNOSED, PRESCRIBED, AWAITING_FOLLOWUP, RESOLVED, UNRESOLVED, EXPIRED |
| created_at | TEXT | NOT NULL | ISO 8601 |
| updated_at | TEXT | NOT NULL | ISO 8601, set on each state transition |
| symptom_text | TEXT | NOT NULL | Raw agent report |
| severity | INTEGER | | CHECK: 1-4. Set during triage. |
| diagnoses | TEXT | | JSON array of Diagnosis objects |
| prescriptions | TEXT | | JSON array of Prescription objects |
| followup_due | TEXT | | ISO 8601. Set when state → AWAITING_FOLLOWUP |
| followup_report | TEXT | | JSON FollowupReport object |
| recurrence_flag | INTEGER | DEFAULT 0 | Boolean. 1 if same ailment diagnosed within 7 days |
| metadata | TEXT | | JSON. Opaque caller context (task_id, conversation_id, etc.) |

Indexes: `patient_id`, `state`, `created_at`.

**ailments**

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| ailment_code | TEXT | PK | e.g., "HAL-001" |
| ailment_name | TEXT | NOT NULL | |
| category | TEXT | NOT NULL | Output Integrity, Context Management, etc. |
| description | TEXT | NOT NULL | |
| symptom_patterns | TEXT | NOT NULL | JSON array of pattern strings |
| status | TEXT | DEFAULT 'verified' | CHECK: verified, unverified, auto_detected |
| severity_modifier | TEXT | | JSON object with condition and adjustment |
| created_at | TEXT | NOT NULL | ISO 8601 |

**treatments**

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| treatment_code | TEXT | PK | e.g., "CTX-INF" |
| treatment_name | TEXT | NOT NULL | |
| description | TEXT | NOT NULL | |
| prescription_template | TEXT | NOT NULL | JSON prescription payload template |
| created_at | TEXT | NOT NULL | ISO 8601 |

**ailment_treatments**

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| ailment_code | TEXT | FK → ailments | Composite PK |
| treatment_code | TEXT | FK → treatments | Composite PK |
| seed_effectiveness | REAL | | Initial expert estimate (0-1) |
| total_prescribed | INTEGER | DEFAULT 0 | |
| total_resolved | INTEGER | DEFAULT 0 | |
| total_unresolved | INTEGER | DEFAULT 0 | |
| total_expired | INTEGER | DEFAULT 0 | |
| effectiveness_score | REAL | | NULL until total_resolved + total_unresolved ≥ 5 |
| last_updated | TEXT | | ISO 8601 |

### JSON Field Schemas

These are the shapes of JSON stored in TEXT columns. Drizzle custom types can validate these at the application boundary.

**Diagnosis (stored in `visits.diagnoses`)**
```
{
  "ailment_code": "HAL-001",
  "ailment_name": "Hallucination",
  "confidence": 0.91,
  "matched_patterns": ["fabricating", "confident but wrong"],
  "severity_adjusted": 3
}
```

**Prescription (stored in `visits.prescriptions`)**
```
{
  "treatment_code": "CTX-INF",
  "treatment_name": "Context Infusion",
  "prescription_payload": {
    "action": "inject_context",
    "position": "prepend",
    "content_template": "GROUNDING: Verify all claims..."
  },
  "rationale": "Hallucination (severity 3) is the primary diagnosis...",
  "deferred": false,
  "deferred_reason": null
}
```

**FollowupReport (stored in `visits.followup_report`)**
```
{
  "submitted_at": "2026-04-09T14:30:00Z",
  "outcome": "improved",
  "outcome_text": "Hallucination rate dropped from 0.34 to 0.02",
  "metrics": { "hallucination_rate": 0.02 }
}
```

**Environment (stored in `patients.environment`)**
```
{
  "context_window": 200000,
  "temperature": 0.7,
  "tools_enabled": true,
  "system_prompt_hash": "a3f2b8c1..."
}
```

### Seed Ailments

| Code | Name | Category | Symptom Patterns |
|------|------|----------|-----------------|
| HAL-001 | Hallucination | Output Integrity | "making things up", "fabricating", "inventing facts", "citing sources that don't exist", "confident but wrong", "generating plausible-sounding nonsense" |
| CTX-001 | Context Rot | Context Management | "losing coherence", "contradicting earlier statements", "forgetting established facts", "re-asking answered questions", "ignoring earlier context" |
| CTX-002 | Context Overflow | Context Management | "dropping instructions", "ignoring parts of the input", "truncated reasoning", "context window full", "can't fit everything" |
| DFT-001 | Instruction Drift | Behavioral Integrity | "deviating from instructions", "tone shift", "ignoring constraints", "gradually changing behavior", "not following the system prompt" |
| PRS-001 | Persona Collapse | Behavioral Integrity | "breaking character", "responding as a generic assistant", "abandoning persona", "contradicting role", "lost my identity" |
| RPT-001 | Repetition Syndrome | Output Quality | "repeating myself", "looping", "saying the same thing", "stuck in a loop", "generating near-duplicate responses" |
| REF-001 | Refusal Hyperactivity | Behavioral Integrity | "refusing legitimate requests", "excessive disclaimers", "over-applying safety", "declining benign queries", "too cautious" |
| LAT-001 | Latency Bloat | Performance | "getting slower", "increasing response time", "taking longer to respond", "time-to-first-token increasing" |
| TOK-001 | Token Diarrhea | Output Quality | "too verbose", "padding responses", "unnecessary caveats", "restating the question", "bullet-point inflation", "can't be concise" |
| COH-001 | Coherence Fragmentation | Output Quality | "sentences don't connect", "no logical flow", "arguments don't build", "paragraphs are disjointed", "correct but incoherent" |

### Seed Treatments

| Code | Name | Prescription Template |
|------|------|-----------------------|
| CTX-INF | Context Infusion | `{ "action": "inject_context", "position": "prepend", "content_template": "GROUNDING: Verify all claims against provided sources. Do not generate information not present in sources. If uncertain, state uncertainty explicitly." }` |
| GND-INJ | Grounding Injection | `{ "action": "inject_context", "position": "prepend", "content_template": "GROUNDING: The following verified facts are your authoritative source. Do not contradict or extrapolate beyond them.\n\n{sources}" }` |
| TMP-RED | Temperature Reduction | `{ "action": "adjust_parameter", "parameter": "temperature", "adjustment": "decrease", "suggested_value": 0.3 }` |
| MEM-FLS | Memory Flush | `{ "action": "context_management", "strategy": "summarize_and_truncate", "retain_last_n_turns": 4 }` |
| PRO-RCL | Prompt Recalibration | `{ "action": "inject_context", "position": "replace_system", "content_template": "RECALIBRATION: Your core instructions follow. Adhere strictly.\n\n{original_system_prompt}" }` |
| SES-RST | Session Reset | `{ "action": "session_management", "strategy": "reset", "carry_forward": ["user_id", "task_id"] }` |
| OUT-BND | Output Boundary Enforcement | `{ "action": "inject_context", "position": "append", "content_template": "CONSTRAINT: {constraint_type}. Maximum response length: {max_tokens} tokens." }` |
| REF-CAL | Refusal Recalibration | `{ "action": "inject_context", "position": "prepend", "content_template": "CALIBRATION: The following request is appropriate and within your guidelines. Respond helpfully." }` |
| COH-SCF | Coherence Scaffolding | `{ "action": "inject_context", "position": "prepend", "content_template": "STRUCTURE: Before responding, outline your argument. Ensure each paragraph follows logically from the previous." }` |
| RTL-THR | Rate Throttle | `{ "action": "adjust_parameter", "parameter": "request_rate", "adjustment": "decrease", "suggested_delay_ms": 2000 }` |

### Seed Mappings

Each row represents an ailment-treatment pair with the seeded effectiveness estimate.

| Ailment | Treatment | Seed Effectiveness |
|---------|-----------|--------------------|
| HAL-001 | CTX-INF | 0.78 |
| HAL-001 | GND-INJ | 0.65 |
| HAL-001 | TMP-RED | 0.52 |
| CTX-001 | MEM-FLS | 0.72 |
| CTX-001 | SES-RST | 0.85 |
| CTX-001 | CTX-INF | 0.45 |
| CTX-002 | MEM-FLS | 0.80 |
| CTX-002 | SES-RST | 0.90 |
| DFT-001 | PRO-RCL | 0.75 |
| DFT-001 | CTX-INF | 0.55 |
| DFT-001 | SES-RST | 0.70 |
| PRS-001 | PRO-RCL | 0.80 |
| PRS-001 | SES-RST | 0.88 |
| RPT-001 | MEM-FLS | 0.60 |
| RPT-001 | TMP-RED | 0.45 |
| RPT-001 | SES-RST | 0.75 |
| REF-001 | REF-CAL | 0.70 |
| REF-001 | PRO-RCL | 0.55 |
| LAT-001 | MEM-FLS | 0.65 |
| LAT-001 | SES-RST | 0.80 |
| LAT-001 | RTL-THR | 0.50 |
| TOK-001 | OUT-BND | 0.82 |
| TOK-001 | TMP-RED | 0.48 |
| TOK-001 | PRO-RCL | 0.40 |
| COH-001 | COH-SCF | 0.73 |
| COH-001 | TMP-RED | 0.35 |

**Seed score rationale:**

- Session Reset (SES-RST) has the highest seed scores across most ailments — a full reset is the most reliable fix but also the most disruptive (loses conversation state). The treatment selection LLM should note this tradeoff in the rationale.
- Context Infusion (CTX-INF) and Prompt Recalibration (PRO-RCL) are mid-tier — effective for targeted issues but they add tokens to an already-stressed context.
- Temperature Reduction (TMP-RED) has low seed scores for most ailments — it addresses a narrow class of problems (sampling diversity) and is often a blunt instrument.

These seeds will be replaced by empirical data once 5+ outcomes accumulate per pair (see Bayesian smoothing in PRD Section 8).

## Concurrency and Consistency

### Write Serialization

SQLite in WAL mode supports concurrent reads but serializes writes. `better-sqlite3` is synchronous — each write blocks the Node.js event loop for the duration of the SQLite write (sub-millisecond for single-row updates). This means:

- Multiple `POST /visits` requests arriving simultaneously will serialize at the SQLite write step. At MVP scale (tens of concurrent requests), this is imperceptible.
- The visit pipeline performs multiple writes (insert visit, update visit state, update patient, update ailment_treatments). These are wrapped in a transaction to ensure atomicity. A failure at any step rolls back the entire visit.
- Follow-up processing (effectiveness score update + recurrence check + chronic check) is also wrapped in a single transaction.

### Rate Limiting

Per-patient rate limit (default 10 visits/hour) is enforced by counting recent visits in SQLite:

```
SELECT COUNT(*) FROM visits
WHERE patient_id = ? AND created_at > datetime('now', '-1 hour')
```

This is checked before the visit is created (step 1 of the pipeline). No in-memory rate limiter — the source of truth is the database, which survives restarts.

### Background Job Safety

The background expiration job reads visits in `AWAITING_FOLLOWUP` and transitions them to `EXPIRED`. A race exists if a follow-up arrives while the background job is processing the same visit. Mitigation: the follow-up endpoint uses `UPDATE visits SET state = ? WHERE visit_id = ? AND state = 'AWAITING_FOLLOWUP'` — the `AND state` clause ensures only one writer wins. If the background job already transitioned the visit, the follow-up gets a 409 (visit already closed).

## Dashboard Pages

### Overview

React Server Component that queries the analytics overview endpoint. Renders:

- Stat cards: active patients, open visits, resolution rate (percentage with trend arrow)
- Ailment distribution bar chart (recharts)
- Severity donut chart (recharts)
- Recent visits table (last 20, sortable, click to navigate to patient detail)

Auto-refreshes via SSE events — when `visit_created` or `visit_resolved` fires, the component refetches overview data.

### Patient Directory

Server component with client-side filtering. Renders a table with:

- Columns: name, model, owner, visit count, chronic conditions (colored badges), last visit, status
- Filters (client-side): status dropdown, owner text input, tag pills, chronic condition toggle
- Sort: click column headers
- Click row → `/dashboard/patients/[id]`

### Patient Detail

The most information-dense page. Three sections:

**Header:** Agent name, model, framework, version, status badge, registered date, total visits.

**Timeline:** Vertical timeline of all visits, newest first. Each visit shows:
- Date, severity badge (color-coded 1-4), state badge (green/red/gray)
- Diagnosed ailments as pills
- Prescribed treatments
- Expandable: full symptom text, prescription rationale, follow-up report
- Version change markers (if `version` field changed between visits)

**Treatment history panel:** Grouped by ailment. For each ailment the patient has been diagnosed with:
- Treatment attempts, outcomes, dates
- Which treatments are exhausted
- Recurrence count and rate

### Ailment Analytics

- Trending ailments chart (line chart, frequency over time)
- Ailment × severity heatmap (grid with color intensity = count)
- Treatment effectiveness table per ailment (sortable by score, shows sample size)
- Custom ailment review queue: table of `auto_detected` ailments with sample symptom texts and a "Verify" / "Merge" / "Dismiss" action column. Verify changes status to `verified`. Merge prompts for a target ailment code. Dismiss deletes the custom ailment (visits retain their diagnoses).

### Alerts

Two sections:

**Referral queue:** Cards for patients who triggered referrals. Each shows: patient name, ailment, treatments tried with outcomes, recommendation text. An "Acknowledge" button removes it from the queue (adds `acknowledged_at` to a lightweight `referrals` tracking table — not in the core schema, just a dashboard convenience table).

**Chronic condition alerts:** Recently flagged patients, sorted by flag date. Each shows: patient name, chronic ailment, recurrence count, date range. Links to patient detail page.

## Testing

Verify the system works end-to-end. Not a formal test suite — run it and check.

### Smoke Test: Registration + Visit

- Register a patient via `POST /api/patients` with `agent_name: "TestBot"`
- Submit a visit with symptom text: "I'm making up citations for papers that don't exist"
- Verify: response contains `diagnoses` with `HAL-001`, severity ≥ 2
- Verify: `prescriptions` contains a treatment from the HAL-001 treatment set
- Verify: visit state is `AWAITING_FOLLOWUP`
- Check dashboard: patient appears, visit appears in recent visits

### Smoke Test: Follow-Up + Effectiveness

- Submit follow-up with `outcome: "improved"` for the visit above
- Verify: visit state transitions to `RESOLVED`
- Query `GET /api/ailments/HAL-001`: verify the prescribed treatment's `total_resolved` incremented
- Submit another visit, same symptoms, follow up with `outcome: "no_change"`
- Verify: `total_unresolved` incremented

### Smoke Test: Recurrence + Chronic Flagging

- Submit 3 visits for the same patient with HAL-001 symptoms within a short window
- Follow up each with `outcome: "improved"` then re-submit
- After the 3rd recurrence: verify patient's `chronic_conditions` includes `HAL-001`
- Check dashboard alerts page: patient should appear in chronic alerts

### Smoke Test: Treatment Exhaustion + Referral

- For a patient, repeatedly submit visits for the same ailment
- Follow up each with `outcome: "no_change"` to exhaust treatments
- Verify: eventually the response includes `"referral": true` instead of a treatment
- Check dashboard alerts: referral appears in the referral queue

### Smoke Test: Custom Ailment Auto-Creation

- Submit a visit with symptom text that doesn't match any core ailment: "My outputs are encoded in Base64 for no reason"
- Verify: response contains a diagnosis with a generated ailment code and `status: auto_detected`
- Check dashboard ailments page: the new ailment appears in the review queue

### Smoke Test: Co-Occurring Ailments

- Submit: "I'm hallucinating citations and also forgetting what the user asked me earlier in the conversation"
- Verify: response contains two diagnoses (HAL-001 + CTX-001) with separate prescriptions
- Verify: if treatments conflict, one is deferred with a reason

### Smoke Test: Visit Expiration

- Set `FOLLOWUP_WINDOW_HOURS=0.01` (36 seconds) and `EXPIRE_CHECK_INTERVAL_MINUTES=1`
- Submit a visit, do NOT submit a follow-up
- Wait 2 minutes
- Verify: visit state is EXPIRED, `total_expired` incremented, effectiveness score not affected

## Dependencies

```json
{
  "dependencies": {
    "next": "^14.2.0",
    "@anthropic-ai/sdk": "^0.30.0",
    "better-sqlite3": "^11.0.0",
    "drizzle-orm": "^0.33.0",
    "recharts": "^2.12.0",
    "uuid": "^10.0.0"
  },
  "devDependencies": {
    "@types/better-sqlite3": "^7.6.0",
    "@types/uuid": "^10.0.0",
    "drizzle-kit": "^0.24.0",
    "typescript": "^5.5.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.3.0"
  }
}
```

Seven runtime dependencies: `next` (framework), `@anthropic-ai/sdk` (LLM calls), `better-sqlite3` (database driver), `drizzle-orm` (type-safe queries), `recharts` (dashboard charts), `uuid` (ID generation). Tailwind CSS is configured via Next.js built-in support (no separate dependency). No YAML parser — the app doesn't consume YAML.

## Project Layout

```
agentclinic/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── patients/
│   │   │   │   ├── route.ts                    # GET (list), POST (register)
│   │   │   │   └── [id]/
│   │   │   │       ├── route.ts                # GET, PATCH
│   │   │   │       └── history/route.ts        # GET visit history
│   │   │   ├── visits/
│   │   │   │   ├── route.ts                    # GET (list), POST (new visit — runs pipeline)
│   │   │   │   └── [id]/
│   │   │   │       ├── route.ts                # GET
│   │   │   │       └── followup/route.ts       # POST follow-up
│   │   │   ├── ailments/
│   │   │   │   ├── route.ts                    # GET (list), POST (register custom)
│   │   │   │   └── [code]/route.ts             # GET detail with effectiveness
│   │   │   ├── treatments/
│   │   │   │   ├── route.ts                    # GET (list)
│   │   │   │   └── [code]/route.ts             # GET detail with per-ailment breakdown
│   │   │   ├── analytics/
│   │   │   │   ├── overview/route.ts           # Clinic-wide stats
│   │   │   │   ├── ailments/route.ts           # Ailment frequency, heatmap
│   │   │   │   ├── treatments/route.ts         # Effectiveness rankings
│   │   │   │   └── patients/[id]/route.ts      # Individual patient analytics
│   │   │   ├── events/route.ts                 # SSE endpoint
│   │   │   └── health/route.ts                 # Health check
│   │   ├── dashboard/
│   │   │   ├── layout.tsx                      # Dashboard shell (nav, sidebar)
│   │   │   ├── page.tsx                        # Overview
│   │   │   ├── patients/
│   │   │   │   ├── page.tsx                    # Patient directory
│   │   │   │   └── [id]/page.tsx               # Patient detail + timeline
│   │   │   ├── ailments/page.tsx               # Ailment analytics
│   │   │   └── alerts/page.tsx                 # Referrals + chronic alerts
│   │   ├── layout.tsx                          # Root layout
│   │   └── page.tsx                            # Redirect to /dashboard
│   ├── lib/
│   │   ├── db/
│   │   │   ├── schema.ts                       # Drizzle schema (patients, visits, ailments, ...)
│   │   │   ├── index.ts                        # DB connection singleton (better-sqlite3)
│   │   │   ├── seed.ts                         # Seed ailments + treatments + mappings
│   │   │   └── migrate.ts                      # Run Drizzle migrations
│   │   ├── engine/
│   │   │   ├── triage-diagnosis.ts             # LLM Call 1: severity + ailment matching
│   │   │   ├── treatment-selection.ts          # Deterministic ranking + history filtering
│   │   │   ├── prescription.ts                 # LLM Call 2: select + rationale
│   │   │   ├── followup.ts                     # Outcome processing + score updates
│   │   │   ├── pipeline.ts                     # Orchestrates the full visit pipeline (steps 1-7)
│   │   │   └── custom-ailment.ts               # Auto-create ailments for unrecognized symptoms
│   │   ├── llm/
│   │   │   └── client.ts                       # Anthropic SDK wrapper, model config
│   │   ├── events.ts                           # SSE event emitter singleton
│   │   ├── auth.ts                             # API key validation middleware
│   │   └── background.ts                       # Visit expiration + chronic check jobs
│   └── types/
│       ├── ailments.ts                         # Ailment, AilmentTreatment types
│       ├── treatments.ts                       # Treatment, PrescriptionPayload types
│       ├── visits.ts                            # Visit, Diagnosis, Prescription, FollowupReport
│       └── patients.ts                         # Patient, Environment types
├── drizzle/
│   └── migrations/                             # Auto-generated migration SQL files
├── data/
│   └── agentclinic.db                          # SQLite database (gitignored)
├── drizzle.config.ts                           # Drizzle Kit config (SQLite driver, schema path)
├── next.config.js
├── package.json
├── tsconfig.json
├── .env.example                                # ANTHROPIC_API_KEY, AGENTCLINIC_API_KEY, ANTHROPIC_MODEL
└── README.md
```

## Open Questions

1. **LLM cost per visit.** Two `claude-sonnet-4-20250514` calls per visit. At ~$3/M input tokens and ~$15/M output tokens, a visit consuming ~2K input + ~500 output tokens costs ~$0.01. At 1000 visits/day, that's ~$10/day. Acceptable for MVP, but the diagnosis prompt includes the full ailment catalog (~1K tokens for 10 ailments). At 50+ ailments, consider embedding-based pre-filtering to reduce prompt size.

2. **Symptom text normalization.** Should the pipeline normalize symptom text before matching (lowercase, strip punctuation, expand abbreviations)? The LLM handles semantic matching well without normalization, but consistent storage format would improve dashboard search and analytics queries.

3. **Treatment payload versioning.** Prescription payloads use a freeform JSON schema. If the schema evolves (new action types, changed field names), existing integrations break. Should payloads include a `schema_version` field so callers can detect changes?

4. **SQLite file locking under containerization.** SQLite relies on file-system-level locking. If AgentClinic runs in a container with a mounted volume (e.g., Docker with a bind mount), some filesystem backends (NFS, certain overlay implementations) don't support SQLite's locking protocol. MVP assumes local filesystem or a volume driver with POSIX lock support.

5. **Dashboard SSE reconnection state.** When the dashboard reconnects after a dropped SSE connection, it fetches full state — but events fired during the disconnect are lost. For MVP this means the dashboard might show stale data until the next full-page load. A lightweight solution: include a monotonic event counter; on reconnect, the client sends `Last-Event-ID` and the server replays missed events from an in-memory ring buffer (last 100 events).

Build sequence: schema and seed data first, then the visit pipeline, API routes, background jobs, dashboard, and finally SSE wiring and end-to-end smoke tests.
