# Model API Calls

These scripts run the unified TCM clinical-case prompt against one model per file. API keys are read only from environment variables and must not be committed.

Default input:

```text
data/benchmark_cases/60_clinical_cases.csv
```

The CSV should contain one patient case per row. The reader auto-detects the case text column from common names such as `题目`, `question`, `case`, `clinical_case`, `病例`, and `病例描述`. It auto-detects `id` when present.

Output columns:

```text
id, 中医诊断, 辨证证型, 西医诊断, 治则, 处方名, 成分与克数, 付数, 用法, 医嘱, raw_response, duration, input_token_count, output_token_count, total_token_count
```

Each output file is append-only and supports resume by `id`.

## Usage

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run a model:

```powershell
python model_api_calls\run_gpt_5.py --input data\benchmark_cases\60_clinical_cases.csv
```

Use `--output`, `--case-column`, `--id-column`, `--limit`, and `--sleep` to customize execution.

## Environment Variables

| Script | Default model | Key variable |
| --- | --- | --- |
| `run_gpt_6_astra.py` | `openai/gpt-6-astra` (OpenRouter) | `OPENROUTER_API_KEY` |
| `run_claude_fable_5_1.py` | `anthropic/claude-fable-5.1` (OpenRouter) | `OPENROUTER_API_KEY` |
| `run_gpt_5.py` | `gpt-5` | `OPENAI_API_KEY` |
| `run_gpt_4o.py` | `gpt-4o` | `OPENAI_API_KEY` |
| `run_openai_o3.py` | `o3` | `OPENAI_API_KEY` |
| `run_gemini_2_5_pro.py` | `gemini-2.5-pro` | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| `run_grok_3.py` | `grok-3` | `XAI_API_KEY` |
| `run_grok_4.py` | `grok-4` | `XAI_API_KEY` |
| `run_claude_opus_4.py` | `claude-opus-4-20250514` | `ANTHROPIC_API_KEY` |
| `run_llama_4_maverick.py` | `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | `TOGETHER_API_KEY` |
| `run_doubao_1_6.py` | `doubao-seed-1.6-250615` | `VOLCENGINE_ARK_API_KEY` or `ARK_API_KEY` |
| `run_doubao_1_6_thinking.py` | `doubao-seed-1.6-thinking-250715` | `VOLCENGINE_ARK_API_KEY` or `ARK_API_KEY` |
| `run_qwen_3_256b.py` | `qwen3-235b-a22b` | `DASHSCOPE_API_KEY` |
| `run_deepseek_r1.py` | `deepseek-reasoner` | `DEEPSEEK_API_KEY` |

Model IDs and base URLs can be overridden with the provider-specific `*_MODEL` and `*_BASE_URL` environment variables defined in each script.

## GPT-6 Astra and Claude Fable 5.1 via OpenRouter

These additions follow the OpenRouter newsletter dated September 28, 2026,
**New: GPT-6 Astra, Claude Fable 5.1, batch discounts, in-region routing, and a shell for any model**.
The older runners remain available as the historical comparison lineup.
The new runners use the existing `openai` dependency; no new SDK is required.

`openrouter.py` only adapts transport. It passes `common.make_messages()` unchanged
and delegates the standard evaluation to `common.run_cases()`: same patient text,
system prompt, nine-field parser, CSV columns, resume-by-id, wall-clock `duration`
(seconds), and token usage mapping. Claude keeps the historical Opus runner's
`max_tokens=4096`; Astra, like the GPT-5 runner, leaves the output cap to the API.
Temperature, seed and reasoning settings remain unspecified, as in those historical
runners. No tools, web search, shell, auto-model router or fallback model list is added.
Provider defaults/routing can change; identical prompts do not guarantee identical
answers. Record the input CSV hash, repository commit, SDK version, run date and any
environment overrides with each experiment. Use a separate output file for every
model/configuration/execution mode: resume checks IDs, not model or configuration.

| Variable | Default / purpose |
| --- | --- |
| `OPENROUTER_API_KEY` | Required only for standard live requests; separate from `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` |
| `OPENROUTER_GPT_6_ASTRA_MODEL` | `openai/gpt-6-astra` |
| `OPENROUTER_CLAUDE_FABLE_5_1_MODEL` | `anthropic/claude-fable-5.1` |
| `OPENROUTER_CLAUDE_FABLE_5_1_MAX_TOKENS` | `4096`; positive integer; changing it creates a different configuration |

The input cases are not distributed in this repository. Supply the same authorized
60-case CSV used for the historical runs. Keep credentials and generated patient
request/response files out of version control; place batch files under `outputs/`.

### Offline checks (no key, no paid requests)

From the repository root:

```powershell
python model_api_calls/run_gpt_6_astra.py --help
python model_api_calls/run_gpt_6_astra.py --input data/benchmark_cases/60_clinical_cases.csv --dry-run
python model_api_calls/run_claude_fable_5_1.py --input data/benchmark_cases/60_clinical_cases.csv --dry-run
python -m unittest discover -s model_api_calls/tests -v
```

`--dry-run` reads cases and existing resume IDs, reports selected/pending counts,
prompt SHA-256 and CSV schema, and makes no network calls or result CSV writes.
Empty case rows are skipped by the shared reader; check that `selected_cases` is 60
for a full benchmark. IDs must be unique. `--limit` selects the first N cases **before**
resume filtering, matching `common.py`; it is not a count of new calls.
The tests use synthetic cases and mocked completions, never real patient data or keys.
Offline checks verify integration, not live model availability or provider acceptance.

### Standard synchronous run (paid; run only when ready)

Set the key in your local shell, then choose one model per command:

```powershell
$env:OPENROUTER_API_KEY = "<your-openrouter-key>"
python model_api_calls/run_gpt_6_astra.py --input data/benchmark_cases/60_clinical_cases.csv --output outputs/gpt_6_astra.csv
python model_api_calls/run_claude_fable_5_1.py --input data/benchmark_cases/60_clinical_cases.csv --output outputs/claude_fable_5_1.csv
```

For Bash, set the key with `export OPENROUTER_API_KEY='<your-openrouter-key>'`.
Standard synchronous execution remains the default. A failed request, blank answer
or token-truncated answer raises before saving that case, so rerunning can retry it.
The OpenAI SDK retains its default HTTP retry policy; inspect provider logs after
ambiguous network failures before retrying a potentially billed request.

### Optional batch preparation and later execution

Use standard execution when per-case timing and immediate append/resume behavior
matter. Batch can suit the 60-case workload when waiting up to 24 hours is acceptable
and token cost matters more than latency. The newsletter reports typically about
50% of standard token prices on supported models and gives
`openai/gpt-6-astra:batch` as the pricing variant. Discounts and model support vary;
check current support/pricing for **each** model before submitting. The newsletter's
standard prices for both new models were $10/M input and $50/M output; these are a
dated reference, not a live quote or total evaluation cost estimate.

Prepare one inline-array request file per model, **offline**:

```powershell
python model_api_calls/run_gpt_6_astra.py --input data/benchmark_cases/60_clinical_cases.csv --output outputs/gpt_6_astra_batch.csv --prepare-batch outputs/gpt_6_astra_batch_requests.json
python model_api_calls/run_claude_fable_5_1.py --input data/benchmark_cases/60_clinical_cases.csv --output outputs/claude_fable_5_1_batch.csv --prepare-batch outputs/claude_fable_5_1_batch_requests.json
```

This exports pending IDs as `custom_id` and exactly the same messages and generation
parameters as standard execution. It does not submit, poll, charge, or write result
CSVs. Existing JSON files are not overwritten. Review the request count (60 for a
fresh full run); do not submit an empty manifest or resubmit an already pending batch.
Preparation does not reserve IDs, so retain the manifest and the returned batch ID.

For later paid execution, the newsletter and
[Batch API announcement](https://openrouter.ai/blog/announcements/batch-api/)
specify `POST https://openrouter.ai/api/v1/batches` with bearer authorization and
the generated JSON. The payload has `endpoint: "/v1/chat/completions"`, the
**standard** model ID at the top level, and `requests: [{custom_id, body}, ...]`.
The `:batch` suffix describes batch pricing; do not pass it to the synchronous runner
or substitute it into the generated payload. Submit the two models as separate batches.
Poll `GET /api/v1/batches/<batch-id>` until `completed`, `failed`, `expired` or
`cancelled`, and retain the inline results, per-request errors and provider metadata.
Consult the [current Batch quickstart](https://openrouter.ai/docs/batch-quickstart)
for the response contract before collection.

This minimal integration provides **batch export only**, not automatic submission or
result import. A later collector must join by `custom_id` (never response order),
parse successful answer text using `common.parse_response()`, map usage to the same
token columns, and append through `common.append_result()` with resume-by-id.
Leave `duration` blank when per-request latency is unavailable; batch queue/poll time
is not the synchronous latency metric. Keep batch outputs separate and failed IDs
retryable. Batch routing/provider differences must be reported in comparisons.

OpenRouter API reference: [OpenAI-compatible quickstart](https://openrouter.ai/docs/quickstart).
