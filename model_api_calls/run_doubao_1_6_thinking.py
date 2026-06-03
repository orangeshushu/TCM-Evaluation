import os

from openai import OpenAI

from common import make_messages, openai_chat_usage, run_cases


MODEL = os.getenv("ARK_MODEL", "doubao-seed-1.6-thinking-250715")
client = OpenAI(
    api_key=os.getenv("VOLCENGINE_ARK_API_KEY") or os.getenv("ARK_API_KEY"),
    base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
)


def call_model(case_text: str):
    response = client.chat.completions.create(
        model=MODEL,
        messages=make_messages(case_text),
    )
    return response.choices[0].message.content.strip(), openai_chat_usage(response)


if __name__ == "__main__":
    run_cases("Doubao 1.6 Thinking", "outputs/doubao_1_6_thinking.csv", call_model)
