import os

from google import genai
from google.genai import types

from common import PROMPT, make_user_text, run_cases


MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))


def call_model(case_text: str):
    response = client.models.generate_content(
        model=MODEL,
        contents=make_user_text(case_text),
        config=types.GenerateContentConfig(system_instruction=PROMPT),
    )
    usage = getattr(response, "usage_metadata", None)
    input_tokens = getattr(usage, "prompt_token_count", "") if usage else ""
    output_tokens = getattr(usage, "candidates_token_count", "") if usage else ""
    total_tokens = getattr(usage, "total_token_count", "") if usage else ""
    return response.text.strip(), {
        "input_token_count": input_tokens,
        "output_token_count": output_tokens,
        "total_token_count": total_tokens,
    }


if __name__ == "__main__":
    run_cases("Gemini 2.5 Pro", "outputs/gemini_2_5_pro.csv", call_model)
