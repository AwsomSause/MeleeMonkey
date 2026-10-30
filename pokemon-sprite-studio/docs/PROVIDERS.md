# Image Providers

## Contract

`backend/generation/providers/base.py` defines `ImageProvider`:

| Method | Purpose |
|---|---|
| `get_capabilities()` | Declares operations, reference limit, mask/alpha/seed support, sizes, async-ness, cost reporting |
| `estimate_cost(request)` | Returns `CostEstimate` labelled `estimate`, `reported` or `free` |
| `generate / edit / generate_variations` | Default implementations raise `UnsupportedOperation` |
| `get_job_status(job_id)` | Only for async providers |
| `run(request)` | Validates against capabilities, then dispatches. Orchestration always calls this |

Adapters receive only references that orchestration has cleared for upload
(`reference_image.allow_external_upload = 1`).

## Adding a provider

1. `backend/generation/providers/<name>.py`, subclass `ImageProvider`.
2. Map provider errors to `RateLimited`, `TransientProviderError`,
   `ContentRejected`, `AuthenticationError`, `InvalidRequest`.
3. Put prices in `assets/presets/provider_prices.json` with a `checked_on`
   date. Prices change, so estimates must say when they were last verified.
4. Contract tests: run `tests/unit/test_providers.py`'s cases against the
   adapter with HTTP mocked (`respx` or recorded fixtures).
5. Optional `@pytest.mark.live` smoke test: one small request.
6. Register in `providers/__init__.py` and document it below.

## Candidates to evaluate (M3)

These are candidates. Their features and prices must be verified from current
vendor docs at implementation time, not assumed.

| Provider | Expected strengths to verify | Notes |
|---|---|---|
| OpenAI image models | Generation + editing with references | Check alpha output and reference limit |
| Google Gemini image models | Multimodal editing, multi-reference | Check transparency support |
| Black Forest Labs FLUX | Strong image quality, edit/kontext models | Usually async (poll) |
| Local SD-compatible (ComfyUI / A1111 API) | Free, offline, LoRA style control | Requires user GPU; `requires_network=False` |

## Selection modes

`manual` · `recommended` (best benchmarked score for the task type) ·
`economical` (cheapest provider whose capabilities fit) · `quality` (highest
benchmarked score regardless of cost). The selected provider is fixed when the
job is queued. A fallback to another provider pauses the job for approval when
its estimated cost is higher or its capabilities differ.

## Benchmark (M3)

A benchmark run sends the same test subject (an original fixture creature +
spec) to every enabled provider and records, per provider: latency, cost,
transparency, reference adherence (human 1–5 rating, plus perceptual
similarity to the reference), pixel-art suitability after M6 processing, and
edit accuracy. Results are stored and shown side by side in Settings → Providers →
Compare. "Cost per successful asset" = total spend ÷ approved outputs.

## Budget guard

Before any paid call, `BudgetGuard.check(estimate)` compares the estimate with
the per-request, daily, monthly and batch limits using `provider_request`
rows. If any limit would be exceeded, the job moves to `PAUSED` with a reason;
nothing is sent. When a provider does not report actual cost, the estimate is
used for budget accounting and the UI labels it "estimated".
