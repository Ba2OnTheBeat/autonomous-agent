"""Safe local opportunity discovery.

The mock catalog stands in for a consented job board/API connector. It never
sends messages, submits proposals, or accesses credentials.
"""
from typing import Any, Dict


MOCK_OPPORTUNITIES = (
    {
        "external_id": "mock-001",
        "title": "Appointment funnel for a local dental clinic",
        "source": "mock-board",
        "url": "https://example.invalid/opportunities/mock-001",
        "summary": "Build inbound lead capture and appointment qualification workflow.",
        "budget": "$1,500-$3,000",
        "keywords": {"appointment": 25, "lead": 20, "automation": 15},
    },
    {
        "external_id": "mock-002",
        "title": "SEO reporting dashboard for a small agency",
        "source": "mock-board",
        "url": "https://example.invalid/opportunities/mock-002",
        "summary": "Automate weekly SEO reporting and client-ready data summaries.",
        "budget": "$800-$1,500",
        "keywords": {"seo": 25, "reporting": 15, "automation": 15},
    },
    {
        "external_id": "mock-003",
        "title": "Generic website redesign",
        "source": "mock-board",
        "url": "https://example.invalid/opportunities/mock-003",
        "summary": "Redesign a marketing website with a modern visual style.",
        "budget": "$500-$1,000",
        "keywords": {"website": 5},
    },
)


def score_opportunity(opportunity: Dict[str, Any]) -> int:
    text = f"{opportunity['title']} {opportunity['summary']}".lower()
    score = min(100, sum(points for keyword, points in opportunity["keywords"].items() if keyword in text))
    return max(0, score)


def discover_mock_opportunities(service: Any) -> list[Dict[str, Any]]:
    discovered = []
    for item in MOCK_OPPORTUNITIES:
        record = {key: value for key, value in item.items() if key != "keywords"}
        record["score"] = score_opportunity(item)
        discovered.append(service.upsert_opportunity(record))
    return discovered
