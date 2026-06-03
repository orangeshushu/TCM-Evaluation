import os

from openai import OpenAI

from common import make_messages, openai_chat_usage, run_cases


MODEL = os.getenv("TOGETHER_MODEL", "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8")
client = OpenAI(
    api_key=os.getenv("TOGETHER_API_KEY"),
    base_url=os.getenv("TOGETHER_BASE_URL", "https://api.together.ai/v1"),
)


def call_model(case_text: str):
    response = client.chat.completions.create(
        model=MODEL,
        messages=make_messages(case_text),
    )
    return response.choices[0].message.content.strip(), openai_chat_usage(response)


if __name__ == "__main__":
    run_cases("Llama 4 Maverick", "outputs/llama_4_maverick.csv", call_model)
