import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json

from app.auditing.auditor import Auditor


def main() -> None:

    query = "What are the Provider's termination rights?"

    auditor = Auditor()

    result = auditor.audit(query)

    print("\n" + "=" * 70)
    print("AUDIT RESULT")
    print("=" * 70)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()