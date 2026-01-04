import argparse
from pathlib import Path
import sys
import json
from textaicheck.text_checkers import AdvancedTextChecker


# Setup path pour imports
file_path = Path(__file__).resolve()
ROOT = file_path.parent


def main():
    invoker = argparse.ArgumentParser(
        description="Docx data extracted for llm analysis."
    )
    invoker.add_argument(
        "--input",
        "-i",
        type=Path,
        default=ROOT / "textaicheck/tmp" / "CorrectionTarget_list_test.json",
        help="Path to extracted/converted json (default: tmp/CorrectionTarget_list_test.json)",
    )
    args = invoker.parse_args()
    try:
        with open(str(args.input), 'r', encoding="utf-8") as file:
            data = json.load(file)
        checker = AdvancedTextChecker()
        corrected_data = checker.reformulate(data)

    except Exception as e:
        print(f"[ERROR] LLM invoke fail: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
