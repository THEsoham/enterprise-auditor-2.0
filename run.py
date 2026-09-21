import sys
import os
from pathlib import Path
import uvicorn

# Fix Windows console encoding — prevents UnicodeEncodeError for emoji/unicode
# characters when running on terminals that default to cp1252.
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    print("\n" + "=" * 60)
    print("🛡️  ENTERPRISE AUDITOR 2.0 — WEB APPLICATION SERVER")
    print("=" * 60)
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))

    print(f"📍 Web App:  http://{host}:{port}")
    print(f"📖 API Docs: http://{host}:{port}/docs")
    print("Press Ctrl+C to stop the server.\n")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
