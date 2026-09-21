import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.debate.debate_graph import DebateEngine


def main():

    query = (
        "What are the Provider's termination rights?"
    )

    engine = DebateEngine(
        max_rounds=3
    )

    result = engine.run(
        query=query
    )

    print("\n")
    print("=" * 70)
    print("FINAL DEBATE RESULT")
    print("=" * 70)

    print(
        json.dumps(
            {
                "final_status":
                    result["final_status"],

                "rounds":
                    len(result["history"]),

                "final_finding":
                    result["finding"],

                "final_verification":
                    result["verification"],
            },
            indent=2
        )
    )


if __name__ == "__main__":
    main()