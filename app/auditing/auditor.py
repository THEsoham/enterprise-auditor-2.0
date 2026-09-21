from app.auditing.finding_generator import FindingGenerator
from app.retrieval.retriever import Retriever


class Auditor:

    def __init__(self):
        self.retriever = Retriever()
        self.generator = FindingGenerator()

    def audit(
        self,
        query: str,
        n_results: int = 5,
    ) -> dict:

        evidence = self.retriever.search(
            query=query,
            n_results=n_results,
        )

        if not evidence:
            return {
                "status": "unsupported",
                "finding": None,
                "evidence": [],
            }

        finding = self.generator.generate(
            query=query,
            evidence=evidence,
        )

        return {
            "status": "generated",
            "finding": finding,
            "evidence": evidence,
        }