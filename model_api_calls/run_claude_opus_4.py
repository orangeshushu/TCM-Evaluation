import os

from anthropic import Anthropic

from common import PROMPT, run_cases


MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-20250514")
MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096"))
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def call_model(case_text: str):
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"请对以下病例给出九个字段的诊断和处方信息：\n{case_text}",
            }
        ],
    )
    answer = "".join(block.text for block in response.content if getattr(block, "type", "") == "text").strip()
    input_tokens = getattr(response.usage, "input_tokens", "")
    output_tokens = getattr(response.usage, "output_tokens", "")
    return answer, {
        "input_token_count": input_tokens,
        "output_token_count": output_tokens,
        "total_token_count": input_tokens + output_tokens if input_tokens != "" and output_tokens != "" else "",
    }


if __name__ == "__main__":
    run_cases("Claude Opus 4", "outputs/claude_opus_4.csv", call_model)
