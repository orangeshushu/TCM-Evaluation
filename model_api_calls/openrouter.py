"""Thin OpenRouter transport; evaluation and CSV handling stay in common.py."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from common import (
    CSV_FIELDS,
    PROMPT,
    build_parser,
    load_processed_ids,
    make_messages,
    openai_chat_usage,
    read_cases,
    require_env,
    run_cases,
)


DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


def request_body(model: str, case_text: str, max_tokens: int | None = None) -> dict:
    body = {"model": model, "messages": make_messages(case_text)}
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    return body


def make_call_model(model: str, max_tokens: int | None = None):
    # Lazy initialization keeps imports, --help and offline paths key-free.
    client = None

    def call_model(case_text: str):
        nonlocal client
        if client is None:
            api_key = require_env("OPENROUTER_API_KEY")
            from openai import OpenAI

            client = OpenAI(
                api_key=api_key,
                base_url=os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL),
            )
        response = client.chat.completions.create(**request_body(model, case_text, max_tokens))
        choices = getattr(response, "choices", None)
        if not choices:
            raise RuntimeError("OpenRouter returned no completion choices; case was not saved.")
        choice = choices[0]
        answer = getattr(choice.message, "content", None)
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("OpenRouter returned no answer text; case was not saved.")
        if getattr(choice, "finish_reason", None) == "length":
            raise RuntimeError("OpenRouter truncated the answer; case was not saved.")
        return answer.strip(), openai_chat_usage(response)

    return call_model


def run_openrouter(
    model_label: str,
    default_model: str,
    model_env: str,
    default_output: str,
    max_tokens_env: str | None = None,
) -> None:
    parser = build_parser(model_label, default_output)
    offline = parser.add_mutually_exclusive_group()
    offline.add_argument("--dry-run", action="store_true", help="Validate cases/resume offline; no API call or CSV write.")
    offline.add_argument("--prepare-batch", metavar="JSON_PATH", help="Export pending requests offline; does not submit a batch.")
    args = parser.parse_args()
    model = os.getenv(model_env, default_model)
    if not model.strip() or model.endswith(":batch"):
        parser.error("Use a standard model ID; batch variants are for the separate Batch API.")
    max_tokens = None
    if max_tokens_env:
        try:
            max_tokens = int(os.getenv(max_tokens_env, "4096"))
            if max_tokens <= 0:
                raise ValueError
        except ValueError:
            parser.error(f"{max_tokens_env} must be a positive integer.")
    if args.limit is not None and args.limit <= 0:
        parser.error("--limit must be a positive integer.")

    # Preflight uses the same reader, limit-before-resume order and resume IDs.
    cases = read_cases(args.input, args.case_column, args.id_column)
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        parser.error("Case IDs must be unique for resume and batch custom_id mapping.")
    if args.limit is not None:
        cases = cases[:args.limit]
    processed = load_processed_ids(args.output)
    pending = [case for case in cases if case["id"] not in processed]

    if args.dry_run:
        print(json.dumps({
            "model": model,
            "base_url": os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL),
            "max_tokens": max_tokens,
            "selected_cases": len(cases),
            "pending_cases": len(pending),
            "prompt_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
            "csv_fields": CSV_FIELDS,
        }, ensure_ascii=False, indent=2))
        return
    if args.prepare_batch:
        path = Path(args.prepare_batch)
        if path.resolve() in {Path(args.input).resolve(), Path(args.output).resolve()}:
            parser.error("Batch JSON must use a separate path from input/output CSV.")
        payload = {
            "endpoint": "/v1/chat/completions",
            "model": model,
            "requests": [
                {"custom_id": case["id"], "body": request_body(model, case["case"], max_tokens)}
                for case in pending
            ],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation avoids accidentally replacing a submitted manifest.
        with path.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print(f"Prepared {len(pending)} requests in {path}; no API calls made.")
        return

    # Normal CLI flags only reach this branch, so common.py remains unchanged.
    run_cases(model_label, default_output, make_call_model(model, max_tokens))
