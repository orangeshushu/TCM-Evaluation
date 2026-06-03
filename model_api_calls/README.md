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
