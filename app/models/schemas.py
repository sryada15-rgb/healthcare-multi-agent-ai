from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    conversation_id: str = Field(min_length=1)
    member_id: str = Field(min_length=1)
    message: str = Field(min_length=2)
    claim_id: str | None = None

class Citation(BaseModel):
    policy_id: str
    section: str
    page: int

class ChatResponse(BaseModel):
    conversation_id: str
    intents: list[str]
    answer: str
    citations: list[Citation] = []
    requires_human_review: bool = False
