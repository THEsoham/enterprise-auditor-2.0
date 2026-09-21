import requests
from pathlib import Path

pdf_path = Path("data/documents/sample_contract.pdf")
if not pdf_path.exists():
    print("PDF not found!")
    exit(1)

print(f"Uploading {pdf_path.name} to http://127.0.0.1:8000/api/upload ...")
with open(pdf_path, "rb") as f:
    files = {"file": (pdf_path.name, f, "application/pdf")}
    res = requests.post("http://127.0.0.1:8000/api/upload", files=files)

print("Status code:", res.status_code)
if res.status_code == 200:
    data = res.json()
    print("Upload and audit succeeded!")
    print("Document:", data.get("filename"))
    print("Score:", data.get("report", {}).get("health", {}).get("health_score"))
    print("Deal breakers count:", data.get("report", {}).get("health", {}).get("deal_breakers_count"))
else:
    print("Error response:", res.text)
