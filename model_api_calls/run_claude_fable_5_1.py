from openrouter import run_openrouter


if __name__ == "__main__":
    run_openrouter(
        "Claude Fable 5.1 (OpenRouter)",
        "anthropic/claude-fable-5.1",
        "OPENROUTER_CLAUDE_FABLE_5_1_MODEL",
        "outputs/claude_fable_5_1.csv",
        max_tokens_env="OPENROUTER_CLAUDE_FABLE_5_1_MAX_TOKENS",
    )
