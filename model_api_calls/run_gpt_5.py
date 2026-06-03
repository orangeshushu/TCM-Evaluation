import os

from openai import OpenAI

from common import PROMPT, make_user_text, openai_response_text, openai_response_usage, run_cases


MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_model(case_text: str):
    response = client.responses.create(
        model=MODEL,
        instructions=PROMPT,
        input=make_user_text(case_text),
    )
    return openai_response_text(response), openai_response_usage(response)


if __name__ == "__main__":
    run_cases("GPT-5", "outputs/gpt_5.csv", call_model)
