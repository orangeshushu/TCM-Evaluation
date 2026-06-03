import os

from openai import OpenAI

from common import make_messages, openai_chat_usage, run_cases


MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner")
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)


def call_model(case_text: str):
    response = client.chat.completions.create(
        model=MODEL,
        messages=make_messages(case_text),
    )
    return response.choices[0].message.content.strip(), openai_chat_usage(response)


if __name__ == "__main__":
    run_cases("DeepSeek-R1", "outputs/deepseek_r1.csv", call_model)
