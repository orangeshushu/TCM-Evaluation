from pathlib import Path
import runpy
import sys


if __name__ == "__main__":
    script = Path(__file__).resolve().parent / "model_api_calls" / "run_doubao_1_6_thinking.py"
    sys.path.insert(0, str(script.parent))
    runpy.run_path(str(script), run_name="__main__")
