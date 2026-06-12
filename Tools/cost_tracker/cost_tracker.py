"""
Zero-dependency cost tracker — monkey-patches OpenAI, Anthropic, and Google
SDK calls to record token usage and estimate costs automatically.
Drop this file next to your notebook and add: import cost_tracker
To disable: comment out that import line.
"""
import functools

import openai.resources.responses.responses as _resp_module
import openai.resources.embeddings as _emb_module

# Pricing per 1M tokens: (input_usd, output_usd)
_PRICING = {
    # OpenAI
    "text-embedding-3-small": (0.020, 0.0),
    "text-embedding-3-large": (0.130, 0.0),
    "gpt-4o":                 (2.50,  10.00),
    "gpt-4o-mini":            (0.150,  0.600),
    "gpt-4.1":                (2.00,   8.00),
    "gpt-4.1-mini":           (0.40,   1.60),
    "gpt-4.1-nano":           (0.10,   0.40),
    "gpt-5.4-nano":           (0.2,    1.25),
    # Anthropic
    "claude-haiku-4-5-20251001":  (0.80,   4.00),
    "claude-sonnet-4-5-20251022": (3.00,  15.00),
    "claude-sonnet-4-6":          (3.00,  15.00),
    "claude-opus-4-8":            (15.00, 75.00),
    # Google Gemini
    "gemini-1.5-flash":   (0.075,  0.30),
    "gemini-1.5-pro":     (1.25,   5.00),
    "gemini-2.0-flash":   (0.10,   0.40),
    "gemini-2.5-flash":   (0.30,   2.50),
    "gemini-2.5-pro":     (1.25,  10.00),
    "text-embedding-004": (0.0,    0.0),
}

SHOW_PRICING_TABLE = False


def _print_pricing_table(records):
    emb_in   = sum(r["input_tokens"]  for r in records if r["type"] == "embedding")
    comp_in  = sum(r["input_tokens"]  for r in records if r["type"] == "completion")
    comp_out = sum(r["output_tokens"] for r in records if r["type"] == "completion")
    embedding_models = [(k, v) for k, v in _PRICING.items() if v[1] == 0.0]
    completion_models = [(k, v) for k, v in _PRICING.items() if v[1] > 0.0]
    col = max(len(k) for k in _PRICING) + 2
    div = "+" + "-" * (col + 2) + "+" + "-" * 12 + "+" + "-" * 13 + "+" + "-" * 15 + "+"

    def row(model, inp, out, cost):
        return f"| {model:<{col}} | {inp:>10} | {out:>11} | {cost:>13} |"

    print(f"\n  Tokens — completion: {comp_in:,} in / {comp_out:,} out  |  embedding: {emb_in:,} in")
    print(div)
    print(row("Model", "Input $/1M", "Output $/1M", "Est. cost ($)"))
    print(div)
    print(row("-- Embedding --", "", "", ""))
    for model, (inp, _) in embedding_models:
        cost = emb_in * inp / 1_000_000
        print(row(model, f"{inp:.3f}", "N/A", f"{cost:.6f}"))
    print(div)
    print(row("-- Completion --", "", "", ""))
    for model, (inp, out) in completion_models:
        cost = comp_in * inp / 1_000_000 + comp_out * out / 1_000_000
        print(row(model, f"{inp:.3f}", f"{out:.3f}", f"{cost:.6f}"))
    print(div + "\n")


class _CostTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self._records = []

    def record(self, model: str, input_tokens: int, output_tokens: int, call_type: str = "completion"):
        prices = _PRICING.get(model)
        if prices is None:
            print(f"[cost_tracker] WARNING: unknown model '{model}' — cost recorded as $0.00")
            prices = (0.0, 0.0)
        in_cost  = input_tokens  * prices[0] / 1_000_000
        out_cost = output_tokens * prices[1] / 1_000_000
        self._records.append({
            "model":         model,
            "input_tokens":  input_tokens,
            "output_tokens": output_tokens,
            "cost_usd":      in_cost + out_cost,
            "type":          call_type,
        })

    def summary(self, show_pricing_table: bool = SHOW_PRICING_TABLE):
        if show_pricing_table:
            _print_pricing_table(self._records)
        if not self._records:
            print("[cost_tracker] No API calls recorded.")
            return
        total_in   = sum(r["input_tokens"]  for r in self._records)
        total_out  = sum(r["output_tokens"] for r in self._records)
        total_cost = sum(r["cost_usd"]      for r in self._records)

        by_model: dict = {}
        for r in self._records:
            m = r["model"]
            if m not in by_model:
                by_model[m] = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
            by_model[m]["calls"]         += 1
            by_model[m]["input_tokens"]  += r["input_tokens"]
            by_model[m]["output_tokens"] += r["output_tokens"]
            by_model[m]["cost_usd"]      += r["cost_usd"]

        print("\n========== COST TRACKER SUMMARY ==========")
        for model, d in by_model.items():
            print(f"  {model}")
            print(f"    calls:         {d['calls']}")
            print(f"    input tokens:  {d['input_tokens']:,}")
            print(f"    output tokens: {d['output_tokens']:,}")
            print(f"    cost:          ${d['cost_usd']:.6f}")
        print("------------------------------------------")
        print(f"  TOTAL input tokens:  {total_in:,}")
        print(f"  TOTAL output tokens: {total_out:,}")
        print(f"  TOTAL cost:          ${total_cost:.6f}")
        print("==========================================\n")


_tracker = _CostTracker()


# ── Patch Responses.create ──────────────────────────────────────────────────
_orig_responses_create = _resp_module.Responses.create


@functools.wraps(_orig_responses_create)
def _patched_responses_create(self, *args, **kwargs):
    response = _orig_responses_create(self, *args, **kwargs)
    try:
        usage = response.usage
        model = kwargs.get("model", "unknown")
        _tracker.record(model, usage.input_tokens, usage.output_tokens)
    except Exception:
        pass
    return response


_resp_module.Responses.create = _patched_responses_create


# ── Patch Embeddings.create ─────────────────────────────────────────────────
_orig_embeddings_create = _emb_module.Embeddings.create


@functools.wraps(_orig_embeddings_create)
def _patched_embeddings_create(self, *args, **kwargs):
    response = _orig_embeddings_create(self, *args, **kwargs)
    try:
        usage = response.usage
        model = kwargs.get("model", "unknown")
        _tracker.record(model, usage.prompt_tokens, 0, call_type="embedding")
    except Exception:
        pass
    return response


_emb_module.Embeddings.create = _patched_embeddings_create


# ── Patch Anthropic Messages.create ────────────────────────────────────────
try:
    import anthropic.resources.messages.messages as _anth_msg_module

    _orig_anth_messages_create = _anth_msg_module.Messages.create

    @functools.wraps(_orig_anth_messages_create)
    def _patched_anth_messages_create(self, *args, **kwargs):
        response = _orig_anth_messages_create(self, *args, **kwargs)
        try:
            usage = response.usage
            model = kwargs.get("model", "unknown")
            _tracker.record(model, usage.input_tokens, usage.output_tokens)
        except Exception:
            pass
        return response

    _anth_msg_module.Messages.create = _patched_anth_messages_create
    print("[cost_tracker] Anthropic patch active.")
except ImportError:
    pass


# ── Patch Google Gemini — newer google-genai SDK ────────────────────────────
try:
    import google.genai.models as _google_models_module

    _orig_google_generate = _google_models_module.Models.generate_content

    @functools.wraps(_orig_google_generate)
    def _patched_google_generate(self, *args, **kwargs):
        response = _orig_google_generate(self, *args, **kwargs)
        try:
            meta = response.usage_metadata
            model = kwargs.get("model", "unknown")
            _tracker.record(model, meta.prompt_token_count, meta.candidates_token_count)
        except Exception:
            pass
        return response

    _google_models_module.Models.generate_content = _patched_google_generate
    print("[cost_tracker] Google (google-genai) patch active.")
except ImportError:
    pass


# ── Patch Google Gemini — older google-generativeai SDK ────────────────────
try:
    import google.generativeai.generative_models as _genai_module

    _orig_genai_generate = _genai_module.GenerativeModel.generate_content

    @functools.wraps(_orig_genai_generate)
    def _patched_genai_generate(self, *args, **kwargs):
        response = _orig_genai_generate(self, *args, **kwargs)
        try:
            meta = response.usage_metadata
            # model name is bound at construction time, not passed per-call
            model = self.model_name
            _tracker.record(model, meta.prompt_token_count, meta.candidates_token_count)
        except Exception:
            pass
        return response

    _genai_module.GenerativeModel.generate_content = _patched_genai_generate
    print("[cost_tracker] Google (google-generativeai) patch active.")
except ImportError:
    pass


# ── Public API ──────────────────────────────────────────────────────────────
def summary(show_pricing_table: bool = SHOW_PRICING_TABLE):
    _tracker.summary(show_pricing_table=show_pricing_table)


def reset():
    _tracker.reset()


print("[cost_tracker] Active — call cost_tracker.summary() to see usage.")
