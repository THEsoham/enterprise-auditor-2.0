import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.pipeline.audit_pipeline import AuditPipeline


def main():
    pdf_path = PROJECT_ROOT / "data" / "documents" / "sample_contract.pdf"
    if not pdf_path.exists():
        print(f"Error: Contract not found at {pdf_path}")
        sys.exit(1)

    pipeline = AuditPipeline(max_debate_rounds=2)

    # Run full autonomous audit (running top 7 comprehensive probes for fast benchmarking)
    result = pipeline.audit(
        pdf_path=pdf_path,
        max_probes=7
    )

    health = result["health"]
    print(f"Health Score: {health.get('health_score')}/100 ({health.get('rating')})")
    print(f"Deal-Breakers: {health.get('deal_breakers_count')}")
    print(f"Watch Out:     {health.get('watch_out_count')}")
    print(f"Protections:   {health.get('protections_count')}")
    print(f"Missing Gap:   {health.get('missing_protections_count')}")
    print(f"Tables:        {len(result.get('tables', []))}")
    print(f"Signature:     {result.get('signature_status', {}).get('overall_status')}")


if __name__ == "__main__":
    main()
