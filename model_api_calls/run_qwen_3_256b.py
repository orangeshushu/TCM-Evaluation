import os

from openai import OpenAI

from common import make_messages, openai_chat_usage, run_cases


MODEL = os.getenv("QWEN_MODEL", "qwen3-235b-a22b")
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
)


def call_model(case_text: str):
    response = client.chat.completions.create(
        model=MODEL,
        messages=make_messages(case_text),
    )
    return response.choices[0].message.content.strip(), openai_chat_usage(response)


if __name__ == "__main__":
    run_cases("Qwen 3-256B", "outputs/qwen_3_256b.csv", call_model)
