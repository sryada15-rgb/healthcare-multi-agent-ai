from typing import TypedDict

class AgentState(TypedDict, total=False):
    conversation_id: str
    member_id: str
    claim_id: str | None
    query: str
    intents: list[str]
    facts: list[str]
    citations: list[dict]
    answer: str
    requires_human_review: bool
