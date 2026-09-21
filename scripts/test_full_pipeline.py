import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.pipeline.audit_pipeline import AuditPipeline


def main():

    queries = [
        "What are the Provider's termination rights?",
        "What is the liability cap?",
        "What happens to backup data after deletion?",
        "Does the contract automatically renew?",
        "Can the Provider use the Customer's name or logo?",
        "What are the Customer's audit rights?",
        "What is the non-solicitation period?",
    ]

    pipeline = AuditPipeline()

    result = pipeline.audit(
        document_name="sample_contract.pdf",
        queries=queries,
    )

    print("\n")
    print("=" * 70)
    print("ENTERPRISE AUDITOR")
    print("=" * 70)

    print("\nHEALTH:")
    print(
        json.dumps(
            result["health"],
            indent=2
        )
    )

    print("\nFINDINGS:")

    for finding in result["findings"]:

        print(
            f"\n[{finding.get('severity', '').upper()}] "
            f"{finding.get('title')}"
        )

        print(
            f"Claim: {finding.get('claim')}"
        )

    print("\nRISK SCORES:")

    print(
        json.dumps(
            result["risk_scores"],
            indent=2
        )
    )

    print("\nGRAPH:")

    print(
        f"Nodes: "
        f"{result['graph'].number_of_nodes()}"
    )

    print(
        f"Edges: "
        f"{result['graph'].number_of_edges()}"
    )


if __name__ == "__main__":
    main()