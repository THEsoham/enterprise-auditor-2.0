import json
from pathlib import Path


class JsonExporter:
    """Exports structured audit reports to formatted JSON files."""

    def __init__(self, output_dir: str = "data/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, report_data: dict, filename: str | None = None) -> Path:
        doc_name = report_data.get("document_name", "audit_report")
        clean_name = Path(doc_name).stem

        if filename:
            file_path = self.output_dir / filename
        else:
            file_path = self.output_dir / f"{clean_name}_audit.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        return file_path
