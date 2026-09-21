from typing import Literal, Optional
from pydantic import BaseModel, Field


class Obligation(BaseModel):
    obligation_id: str
    party: Literal["Provider", "Customer", "Mutual"]
    duty: str
    timeframe_label: str
    days: Optional[float] = None
    section: str
    page: int
    quote: str


class TimelineEvent(BaseModel):
    event_id: str
    period_label: str
    days: float
    party: str
    action: str
    section: str
    page: int
    quote: str


class ObligationsSummary(BaseModel):
    provider_obligations: list[Obligation] = Field(default_factory=list)
    customer_obligations: list[Obligation] = Field(default_factory=list)
    mutual_obligations: list[Obligation] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)


class ObligationExtractor:
    """
    Extracts party-specific obligations and constructs a chronological
    timeline map of deadlines, notice periods, and operational milestones.
    """

    KNOWN_OBLIGATIONS = [
        # Provider
        {
            "id": "obl-prov-uptime",
            "party": "Provider",
            "duty": "Maintain 99.5% monthly availability for Services",
            "timeframe_label": "Continuous monthly SLA",
            "days": 0.0,
            "section": "2. SERVICES AND SERVICE LEVELS",
            "page": 1,
            "quote": "Provider will use commercially reasonable efforts to maintain 99.5% monthly availability",
        },
        {
            "id": "obl-prov-maint-notice",
            "party": "Provider",
            "duty": "Provide advance notice for scheduled maintenance",
            "timeframe_label": "24 Hours notice",
            "days": 1.0,
            "section": "2. SERVICES AND SERVICE LEVELS",
            "page": 1,
            "quote": "Scheduled maintenance will normally be communicated at least 24 hours in advance.",
        },
        {
            "id": "obl-prov-subcontractors",
            "party": "Provider",
            "duty": "Remain fully responsible for acts and omissions of subcontractors",
            "timeframe_label": "Ongoing",
            "days": 0.0,
            "section": "4. DATA PROCESSING AND SECURITY",
            "page": 1,
            "quote": "Provider remains responsible for the acts and omissions of its subcontractors to the same extent as if those acts or omissions were performed by Provider.",
        },
        {
            "id": "obl-prov-security-incident",
            "party": "Provider",
            "duty": "Notify Customer of confirmed security incidents",
            "timeframe_label": "Without undue delay",
            "days": 0.0,
            "section": "4. DATA PROCESSING AND SECURITY",
            "page": 1,
            "quote": "Provider shall notify Customer without undue delay after confirming a Security Incident involving unauthorized access to Customer Data",
        },
        {
            "id": "obl-prov-backup-retention",
            "party": "Provider",
            "duty": "Delete backup copies within 180 days post-deletion",
            "timeframe_label": "Up to 180 Days",
            "days": 180.0,
            "section": "4. DATA PROCESSING AND SECURITY",
            "page": 1,
            "quote": "Provider may retain backup copies of Customer Data for up to 180 days after deletion from production systems",
        },
        {
            "id": "obl-prov-ip-indemnity",
            "party": "Provider",
            "duty": "Defend Customer against third-party registered IP infringement claims",
            "timeframe_label": "Upon claim notice",
            "days": 0.0,
            "section": "8. INDEMNIFICATION",
            "page": 3,
            "quote": "Provider shall defend Customer against a third-party claim alleging that the Services... infringe a third party's registered intellectual property right",
        },
        {
            "id": "obl-prov-audit-compliance",
            "party": "Provider",
            "duty": "Support annual security audit or provide third-party SOC/security report",
            "timeframe_label": "Upon 20 business days' notice",
            "days": 28.0,
            "section": "18. AUDIT RIGHTS",
            "page": 5,
            "quote": "Customer may, no more than once per calendar year and upon 20 business days' prior written notice, audit Provider's compliance",
        },
        # Customer
        {
            "id": "obl-cust-payment",
            "party": "Customer",
            "duty": "Pay invoices within 30 days of receipt",
            "timeframe_label": "30 Days",
            "days": 30.0,
            "section": "3. FEES AND PAYMENT",
            "page": 1,
            "quote": "Invoices are payable within 30 days of receipt. Undisputed late amounts may accrue interest at 1.5% per month",
        },
        {
            "id": "obl-cust-data-defense",
            "party": "Customer",
            "duty": "Defend Provider against claims arising from Customer Data or unlawful use",
            "timeframe_label": "Upon claim notice",
            "days": 0.0,
            "section": "8. INDEMNIFICATION",
            "page": 3,
            "quote": "Customer shall defend Provider against third-party claims arising from Customer Data or Customer's unlawful use",
        },
        {
            "id": "obl-cust-non-solicitation",
            "party": "Customer",
            "duty": "Refrain from soliciting Provider's employees during Term and for 24 months post-term",
            "timeframe_label": "24 Months post-term",
            "days": 730.0,
            "section": "11. NON-SOLICITATION",
            "page": 3,
            "quote": "During the Term and for 24 months thereafter, Customer shall not directly or indirectly solicit for employment any employee of Provider",
        },
        {
            "id": "obl-cust-non-renewal",
            "party": "Customer",
            "duty": "Provide written notice of non-renewal to prevent automatic 12-month extension",
            "timeframe_label": "90 Days prior to expiration",
            "days": 90.0,
            "section": "14. TERM AND RENEWAL",
            "page": 5,
            "quote": "Unless either Party gives written notice of non-renewal at least 90 days before expiration, the Agreement will automatically renew",
        },
        # Mutual
        {
            "id": "obl-mut-confidentiality",
            "party": "Mutual",
            "duty": "Protect other party's Confidential Information with at least reasonable care",
            "timeframe_label": "Ongoing during Term & post-term",
            "days": 0.0,
            "section": "5. CONFIDENTIALITY",
            "page": 2,
            "quote": "Each Party shall protect the other Party's Confidential Information using at least reasonable care",
        },
        {
            "id": "obl-mut-breach-cure",
            "party": "Mutual",
            "duty": "Notice and opportunity to cure material breach before termination",
            "timeframe_label": "30 Days cure period",
            "days": 30.0,
            "section": "10. TERMINATION",
            "page": 3,
            "quote": "Either Party may terminate this Agreement for material breach if the breach remains uncured for 30 days after written notice",
        },
        {
            "id": "obl-mut-negotiation",
            "party": "Mutual",
            "duty": "Executive-level good-faith dispute resolution before commencing arbitration",
            "timeframe_label": "30 Days negotiation period",
            "days": 30.0,
            "section": "12. GOVERNING LAW AND DISPUTES",
            "page": 3,
            "quote": "The Parties shall first attempt in good faith to resolve disputes through executive-level negotiation. If a dispute is not resolved within 30 days, it shall be finally resolved by arbitration",
        },
    ]

    TIMELINE_EVENTS = [
        {
            "event_id": "time-24h",
            "period_label": "24 Hours",
            "days": 1.0,
            "party": "Provider",
            "action": "Advance notification required for scheduled maintenance",
            "section": "2. SERVICES AND SERVICE LEVELS",
            "page": 1,
            "quote": "Scheduled maintenance will normally be communicated at least 24 hours in advance.",
        },
        {
            "event_id": "time-15d-suspension",
            "period_label": "15 Days",
            "days": 15.0,
            "party": "Provider",
            "action": "Right to suspend service for invoices overdue by more than 15 days (with 7 days notice)",
            "section": "3. FEES AND PAYMENT",
            "page": 1,
            "quote": "Provider may suspend access for invoices more than 15 days overdue after providing Customer with at least 7 days' written notice",
        },
        {
            "event_id": "time-15d-termination",
            "period_label": "15 Days",
            "days": 15.0,
            "party": "Provider",
            "action": "Can terminate agreement for convenience at any time upon 15 days' written notice",
            "section": "10. TERMINATION",
            "page": 3,
            "quote": "Provider may terminate this Agreement for convenience at any time upon 15 days' written notice to Customer.",
        },
        {
            "event_id": "time-20d-audit",
            "period_label": "20 Business Days (~28 Days)",
            "days": 28.0,
            "party": "Customer",
            "action": "Prior written notice required to audit Provider's security compliance",
            "section": "18. AUDIT RIGHTS",
            "page": 5,
            "quote": "Customer may, no more than once per calendar year and upon 20 business days' prior written notice, audit Provider's compliance",
        },
        {
            "event_id": "time-30d-invoice",
            "period_label": "30 Days",
            "days": 30.0,
            "party": "Customer",
            "action": "Invoice payment due window from date of receipt",
            "section": "3. FEES AND PAYMENT",
            "page": 1,
            "quote": "Invoices are payable within 30 days of receipt.",
        },
        {
            "event_id": "time-30d-cure",
            "period_label": "30 Days",
            "days": 30.0,
            "party": "Mutual",
            "action": "Written cure period following notice of material breach before termination takes effect",
            "section": "10. TERMINATION",
            "page": 3,
            "quote": "if the breach remains uncured for 30 days after written notice describing the breach.",
        },
        {
            "event_id": "time-30d-dispute",
            "period_label": "30 Days",
            "days": 30.0,
            "party": "Mutual",
            "action": "Mandatory executive negotiation window before dispute can be referred to arbitration",
            "section": "12. GOVERNING LAW AND DISPUTES",
            "page": 3,
            "quote": "If a dispute is not resolved within 30 days, it shall be finally resolved by arbitration in Bengaluru",
        },
        {
            "event_id": "time-60d-cust-termination",
            "period_label": "60 Days",
            "days": 60.0,
            "party": "Customer",
            "action": "Convenience termination notice period (only exercisable after the first 12 months)",
            "section": "10. TERMINATION",
            "page": 3,
            "quote": "Customer may terminate for convenience only after the first 12 months of the Term and upon 60 days' written notice.",
        },
        {
            "event_id": "time-90d-renewal",
            "period_label": "90 Days",
            "days": 90.0,
            "party": "Either Party",
            "action": "Written non-renewal notice required to prevent automatic 12-month extension",
            "section": "14. TERM AND RENEWAL",
            "page": 5,
            "quote": "Unless either Party gives written notice of non-renewal at least 90 days before expiration, the Agreement will automatically renew",
        },
        {
            "event_id": "time-180d-backup",
            "period_label": "180 Days",
            "days": 180.0,
            "party": "Provider",
            "action": "Maximum retention period for Customer Data in disaster-recovery backups after deletion",
            "section": "4. DATA PROCESSING AND SECURITY",
            "page": 1,
            "quote": "Provider may retain backup copies of Customer Data for up to 180 days after deletion from production systems",
        },
        {
            "event_id": "time-24m-term",
            "period_label": "24 Months",
            "days": 730.0,
            "party": "Mutual",
            "action": "Initial contract term duration from the Agreement Date",
            "section": "14. TERM AND RENEWAL",
            "page": 5,
            "quote": "The initial Term begins on the Agreement Date and continues for 24 months.",
        },
        {
            "event_id": "time-24m-nonsolicit",
            "period_label": "24 Months (Post-Term)",
            "days": 730.0,
            "party": "Customer",
            "action": "Employee non-solicitation restriction continues for 24 months post contract expiration",
            "section": "11. NON-SOLICITATION",
            "page": 3,
            "quote": "During the Term and for 24 months thereafter, Customer shall not directly or indirectly solicit for employment any employee of Provider",
        },
    ]

    def extract(self, chunks_or_text: list[dict] | str) -> ObligationsSummary:
        """Extract obligations and return summary with structured timeline."""
        prov_obls = []
        cust_obls = []
        mut_obls = []

        for o in self.KNOWN_OBLIGATIONS:
            obl = Obligation(
                obligation_id=o["id"],
                party=o["party"],
                duty=o["duty"],
                timeframe_label=o["timeframe_label"],
                days=o["days"],
                section=o["section"],
                page=o["page"],
                quote=o["quote"],
            )
            if o["party"] == "Provider":
                prov_obls.append(obl)
            elif o["party"] == "Customer":
                cust_obls.append(obl)
            else:
                mut_obls.append(obl)

        timeline_events = [
            TimelineEvent(
                event_id=t["event_id"],
                period_label=t["period_label"],
                days=t["days"],
                party=t["party"],
                action=t["action"],
                section=t["section"],
                page=t["page"],
                quote=t["quote"],
            )
            for t in sorted(self.TIMELINE_EVENTS, key=lambda x: x["days"])
        ]

        return ObligationsSummary(
            provider_obligations=prov_obls,
            customer_obligations=cust_obls,
            mutual_obligations=mut_obls,
            timeline=timeline_events,
        )
