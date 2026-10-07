from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.core.config import get_settings
from app.db.seed import init_and_seed
from app.db.database import SessionLocal
from app.models.db_models import AuditLog
from app.models.schemas import ChatRequest, ChatResponse
from app.rag.milvus_store import PolicyStore
from app.agents.nodes import set_policy_store
from app.agents.graph import build_graph
from app.services.redis_memory import ConversationMemory

settings = get_settings()
graph = build_graph()
memory: ConversationMemory | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global memory
    init_and_seed()
    store = PolicyStore()
    store.ingest_sample_policies()
    set_policy_store(store)
    memory = ConversationMemory()
    yield

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        history = memory.get(req.conversation_id) if memory else []
        state = {
            "conversation_id": req.conversation_id,
            "member_id": req.member_id,
            "claim_id": req.claim_id,
            "query": req.message,
            "facts": [f"Recent conversation: {history[-2:]}" ] if history else [],
            "citations": [],
            "requires_human_review": False,
        }
        result = graph.invoke(state)
        if memory:
            memory.append(req.conversation_id, "user", req.message)
            memory.append(req.conversation_id, "assistant", result["answer"])
        with SessionLocal() as db:
            db.add(AuditLog(conversation_id=req.conversation_id, query=req.message, route=",".join(result.get("intents", [])), answer=result["answer"]))
            db.commit()
        return ChatResponse(
            conversation_id=req.conversation_id,
            intents=result.get("intents", []),
            answer=result["answer"],
            citations=result.get("citations", []),
            requires_human_review=result.get("requires_human_review", False),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent workflow failed: {exc}") from exc
