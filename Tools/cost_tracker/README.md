# cost_tracker

A single-file, zero-config cost tracker for OpenAI, Anthropic, and Google Gemini API calls in Python notebooks and scripts.

## How it works

`import cost_tracker` monkey-patches the SDK methods for all three providers at import time. Every subsequent API call is intercepted, token counts are read from the response, and cost is computed using the pricing table embedded in the file. No wrappers, no extra arguments required.

## Setup

Copy `cost_tracker.py` into the same directory as your notebook or script, then add one line at the top:

```python
import cost_tracker
```

To stop tracking, comment that line out.

## Usage

```python
import cost_tracker

# OpenAI (Responses API)
response = openai_client.responses.create(model="gpt-4.1-mini", input="Hello")

# Anthropic
response = anthropic_client.messages.create(
    model="claude-sonnet-4-6", max_tokens=256, messages=[...]
)

# Google Gemini (google-genai)
response = google_client.models.generate_content(model="gemini-2.0-flash", contents="Hello")

# Print a summary of all calls made so far
cost_tracker.summary()
```

Example output:

```
========== COST TRACKER SUMMARY ==========
  gpt-4.1-mini
    calls:         3
    input tokens:  1,240
    output tokens: 318
    cost:          $0.001007
  claude-sonnet-4-6
    calls:         1
    input tokens:  512
    output tokens: 128
    cost:          $0.003456
------------------------------------------
  TOTAL input tokens:  1,752
  TOTAL output tokens: 446
  TOTAL cost:          $0.004463
==========================================
```

## Public API

| Function | Description |
|---|---|
| `cost_tracker.summary()` | Print per-model and total token/cost breakdown |
| `cost_tracker.summary(show_pricing_table=True)` | Also show a full what-if pricing table across all known models |
| `cost_tracker.reset()` | Clear all recorded calls (useful between notebook sections) |

## Supported models

| Provider | Model | Input $/1M | Output $/1M |
|---|---|---|---|
| OpenAI | gpt-4o | 2.50 | 10.00 |
| OpenAI | gpt-4o-mini | 0.15 | 0.60 |
| OpenAI | gpt-4.1 | 2.00 | 8.00 |
| OpenAI | gpt-4.1-mini | 0.40 | 1.60 |
| OpenAI | gpt-4.1-nano | 0.10 | 0.40 |
| OpenAI | gpt-5.4-nano | 0.20 | 1.25 |
| OpenAI | text-embedding-3-small | 0.020 | — |
| OpenAI | text-embedding-3-large | 0.130 | — |
| Anthropic | claude-haiku-4-5-20251001 | 0.80 | 4.00 |
| Anthropic | claude-sonnet-4-5-20251022 | 3.00 | 15.00 |
| Anthropic | claude-sonnet-4-6 | 3.00 | 15.00 |
| Anthropic | claude-opus-4-8 | 15.00 | 75.00 |
| Google | gemini-1.5-flash | 0.075 | 0.30 |
| Google | gemini-1.5-pro | 1.25 | 5.00 |
| Google | gemini-2.0-flash | 0.10 | 0.40 |
| Google | gemini-2.5-flash | 0.30 | 2.50 |
| Google | gemini-2.5-pro | 1.25 | 10.00 |
| Google | text-embedding-004 | 0.0 | — |

## Adding a model

Open `cost_tracker.py` and add one line to `_PRICING`:

```python
"your-model-id": (input_usd_per_1M, output_usd_per_1M),
```

## Provider SDK compatibility

Each provider's patch is applied only if the corresponding SDK is installed. Missing SDKs are silently skipped — the tracker still works for whichever providers are available.

| Provider | SDK package | Patched method |
|---|---|---|
| OpenAI | `openai` | `Responses.create`, `Embeddings.create` |
| Anthropic | `anthropic` | `Messages.create` |
| Google (new) | `google-genai` | `Models.generate_content` |
| Google (legacy) | `google-generativeai` | `GenerativeModel.generate_content` |
