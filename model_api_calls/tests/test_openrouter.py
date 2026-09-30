"""Offline contract tests: synthetic cases and a fake SDK, no network or keys."""
import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

MODEL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODEL_DIR))

import common
import openrouter


ANSWER = "\n".join(f"{field}：测试内容" for field in common.OUTPUT_FIELDS)


def completion(content=ANSWER, finish_reason="stop", usage=True):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content), finish_reason=finish_reason)],
        usage=SimpleNamespace(prompt_tokens=100, completion_tokens=200, total_tokens=300) if usage else None,
    )


class OpenRouterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "cases.csv"
        self.output = self.root / "results.csv"
        with self.input.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["case_id", "病例描述"])
            writer.writeheader()
            writer.writerows({"case_id": str(i), "病例描述": f"合成病例 {i}"} for i in range(1, 61))

    def argv(self, *extra):
        return ["runner", "--input", str(self.input), "--output", str(self.output), "--sleep", "0", *extra]

    def run_entry(self, model="openai/gpt-6-astra", cap_env=None):
        openrouter.run_openrouter("test", model, "TEST_OPENROUTER_MODEL", str(self.output), cap_env)

    def sdk(self, response=None):
        client = Mock()
        client.chat.completions.create.return_value = response if response is not None else completion()
        constructor = Mock(return_value=client)
        return client, constructor, {"openai": SimpleNamespace(OpenAI=constructor)}

    def test_request_preserves_prompt_and_messages(self):
        for model in ["openai/gpt-6-astra", "anthropic/claude-fable-5.1"]:
            body = openrouter.request_body(model, "合成病例")
            self.assertEqual(body, {"model": model, "messages": common.make_messages("合成病例")})
            self.assertEqual(body["messages"][0]["content"], common.PROMPT)
        self.assertEqual(openrouter.request_body("model", "case", 4096)["max_tokens"], 4096)

    def test_lazy_client_usage_and_explicit_base_url(self):
        client, constructor, sdk = self.sdk()
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "offline-fake", "OPENROUTER_BASE_URL": "https://example.invalid/api/v1"}, clear=True), patch.dict(sys.modules, sdk):
            call = openrouter.make_call_model("openai/gpt-6-astra")
            constructor.assert_not_called()
            answer, usage = call("case")
            call("another case")
        constructor.assert_called_once_with(api_key="offline-fake", base_url="https://example.invalid/api/v1")
        self.assertEqual(client.chat.completions.create.call_args_list[0].kwargs, openrouter.request_body("openai/gpt-6-astra", "case"))
        self.assertEqual(answer, ANSWER)
        self.assertEqual(usage, {"input_token_count": 100, "output_token_count": 200, "total_token_count": 300})

    def test_missing_key_fails_without_creating_client(self):
        _, constructor, sdk = self.sdk()
        with patch.dict(os.environ, {}, clear=True), patch.dict(sys.modules, sdk):
            with self.assertRaisesRegex(RuntimeError, "OPENROUTER_API_KEY"):
                openrouter.make_call_model("model")("case")
        constructor.assert_not_called()

    def test_absent_usage_stays_blank(self):
        _, _, sdk = self.sdk(completion(usage=False))
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "offline-fake"}, clear=True), patch.dict(sys.modules, sdk):
            _, usage = openrouter.make_call_model("model")("case")
        self.assertEqual(usage, dict.fromkeys(["input_token_count", "output_token_count", "total_token_count"], ""))

    def test_blank_truncated_and_error_responses_are_not_saved(self):
        responses = [completion(None), completion(" "), completion(finish_reason="length"), SimpleNamespace(choices=[])]
        for response in responses:
            with self.subTest(response=response):
                _, _, sdk = self.sdk(response)
                with patch.dict(os.environ, {"OPENROUTER_API_KEY": "offline-fake"}, clear=True), patch.dict(sys.modules, sdk), patch.object(sys, "argv", self.argv("--limit", "1")):
                    with self.assertRaises(RuntimeError):
                        self.run_entry()
                self.assertFalse(self.output.exists())

    def test_api_exception_leaves_case_retryable(self):
        client, _, sdk = self.sdk()
        client.chat.completions.create.side_effect = RuntimeError("mock HTTP failure")
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "offline-fake"}, clear=True), patch.dict(sys.modules, sdk), patch.object(sys, "argv", self.argv("--limit", "1")):
            with self.assertRaisesRegex(RuntimeError, "HTTP failure"):
                self.run_entry()
        self.assertFalse(self.output.exists())

    def test_full_60_cases_csv_and_resume_for_both_models(self):
        for model, cap_env, cap in [("openai/gpt-6-astra", None, None), ("anthropic/claude-fable-5.1", "TEST_CLAUDE_CAP", 4096)]:
            with self.subTest(model=model):
                self.output = self.root / ("astra.csv" if cap_env is None else "fable.csv")
                client, constructor, sdk = self.sdk()
                with patch.dict(os.environ, {"OPENROUTER_API_KEY": "offline-fake"}, clear=True), patch.dict(sys.modules, sdk), patch.object(sys, "argv", self.argv()):
                    self.run_entry(model, cap_env)
                    self.run_entry(model, cap_env)
                self.assertEqual(client.chat.completions.create.call_count, 60)
                constructor.assert_called_once_with(api_key="offline-fake", base_url=openrouter.DEFAULT_BASE_URL)
                self.assertEqual(client.chat.completions.create.call_args_list[0].kwargs, openrouter.request_body(model, "合成病例 1", cap))
                with self.output.open(encoding="utf-8-sig", newline="") as handle:
                    reader = csv.DictReader(handle)
                    rows = list(reader)
                    self.assertEqual(reader.fieldnames, common.CSV_FIELDS)
                self.assertEqual([row["id"] for row in rows], [str(i) for i in range(1, 61)])
                self.assertEqual(rows[0]["raw_response"], ANSWER)
                for field in common.OUTPUT_FIELDS:
                    self.assertEqual(rows[0][field], "测试内容")
                self.assertEqual(rows[0]["total_token_count"], "300")
                self.assertGreaterEqual(float(rows[0]["duration"]), 0)

    def test_cli_help_dry_run_and_batch_are_key_free(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("OPENROUTER_", "OPENAI_"))}
        for script, model, cap in [("run_gpt_6_astra.py", "openai/gpt-6-astra", None), ("run_claude_fable_5_1.py", "anthropic/claude-fable-5.1", 4096)]:
            cmd = [sys.executable, str(MODEL_DIR / script)]
            help_result = subprocess.run(cmd + ["--help"], env=env, capture_output=True, text=True, check=True)
            self.assertIn("--dry-run", help_result.stdout)
            flags = self.argv()[1:]
            result = subprocess.run(cmd + flags + ["--dry-run"], env=env, capture_output=True, text=True, check=True)
            summary = json.loads(result.stdout)
            self.assertEqual((summary["selected_cases"], summary["pending_cases"]), (60, 60))
            self.assertEqual(summary["model"], model)
            self.assertEqual(summary["csv_fields"], common.CSV_FIELDS)
            manifest = self.root / (script + ".json")
            subprocess.run(cmd + flags + ["--prepare-batch", str(manifest)], env=env, capture_output=True, text=True, check=True)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["endpoint"], "/v1/chat/completions")
            self.assertEqual(payload["model"], model)
            self.assertEqual(len(payload["requests"]), 60)
            self.assertEqual(payload["requests"][0], {"custom_id": "1", "body": openrouter.request_body(model, "合成病例 1", cap)})
        self.assertFalse(self.output.exists())

    def test_batch_resume_limit_and_exclusive_manifest(self):
        common.append_result(str(self.output), {"id": "1"})
        manifest = self.root / "batch.json"
        with patch.dict(os.environ, {}, clear=True), patch.object(sys, "argv", self.argv("--limit", "3", "--prepare-batch", str(manifest))):
            self.run_entry()
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual([r["custom_id"] for r in payload["requests"]], ["2", "3"])
            with self.assertRaises(FileExistsError):
                self.run_entry()
        self.assertEqual(common.load_processed_ids(str(self.output)), {"1"})

    def test_model_and_cap_overrides(self):
        client, _, sdk = self.sdk()
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "offline-fake", "TEST_OPENROUTER_MODEL": "anthropic/pinned-snapshot", "TEST_CLAUDE_CAP": "8192"}, clear=True), patch.dict(sys.modules, sdk), patch.object(sys, "argv", self.argv("--limit", "1")):
            self.run_entry("anthropic/claude-fable-5.1", "TEST_CLAUDE_CAP")
        self.assertEqual(client.chat.completions.create.call_args.kwargs["model"], "anthropic/pinned-snapshot")
        self.assertEqual(client.chat.completions.create.call_args.kwargs["max_tokens"], 8192)

    def test_duplicate_ids_and_batch_model_are_rejected_offline(self):
        self.input.write_text("id,case\n1,synthetic A\n1,synthetic B\n", encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True), patch.object(sys, "argv", self.argv("--dry-run")):
            with self.assertRaises(SystemExit):
                self.run_entry()
        with patch.dict(os.environ, {"TEST_OPENROUTER_MODEL": "openai/gpt-6-astra:batch"}, clear=True), patch.object(sys, "argv", self.argv("--dry-run")):
            with self.assertRaises(SystemExit):
                self.run_entry()


if __name__ == "__main__":
    unittest.main()
