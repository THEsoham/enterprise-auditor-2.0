import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.auditing.auditor import Auditor
from app.verification.verifier import GeminiVerifier


def main():
    query = "What are the Provider's termination rights?"

    print("Running OpenAI Auditor...", flush=True)

    auditor = Auditor()

    audit_result = auditor.audit(
        query=query,
        n_results=3
    )

    print("\nAUDITOR RESULT:", flush=True)

    print(
        json.dumps(
            audit_result["finding"],
            indent=2
        ),
        flush=True
    )

    if audit_result["status"] != "generated":
        print("\nNo finding generated.", flush=True)
        return

    print("\nRunning Gemini verification...", flush=True)

    verifier = GeminiVerifier()

    verification = verifier.verify(
        finding=audit_result["finding"],
        evidence=audit_result["evidence"]
    )

    print("\nGEMINI VERIFICATION:", flush=True)

    print(
        json.dumps(
            verification,
            indent=2
        ),
        flush=True
    )


if __name__ == "__main__":
    main()