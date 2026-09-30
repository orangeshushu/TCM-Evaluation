from openrouter import run_openrouter


if __name__ == "__main__":
    run_openrouter(
        "GPT-6 Astra (OpenRouter)",
        "openai/gpt-6-astra",
        "OPENROUTER_GPT_6_ASTRA_MODEL",
        "outputs/gpt_6_astra.csv",
    )
