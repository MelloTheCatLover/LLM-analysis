from typing import TypedDict, Optional

class DocumentResult(TypedDict):
    filename: str
    claimed: str
    detected: str
    description: str
    similarity: float
    match: bool
    text: str
    analysis: dict
    person: Optional[dict]
