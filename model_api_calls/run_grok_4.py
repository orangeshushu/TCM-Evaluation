import os

from openai import OpenAI

from common import make_messages, openai_chat_usage, run_cases


MODEL = os.getenv("XAI_MODEL", "grok-4")
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url=os.getenv("XAI_BASE_URL", "https://api.x.ai/v1"),
)


def call_model(case_text: str):
    response = client.chat.completions.create(
        model=MODEL,
        messages=make_messages(case_text),
    )
    return response.choices[0].message.content.strip(), openai_chat_usage(response)


if __name__ == "__main__":
    run_cases("Grok 4", "outputs/grok_4.csv", call_model)
