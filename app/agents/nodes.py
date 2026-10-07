import re
from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.db_models import Claim, PriorAuthorization
from app.rag.milvus_store import PolicyStore
from app.services.llm import generate_answer

policy_store: PolicyStore | None = None

def set_policy_store(store: PolicyStore):
    global policy_store
    policy_store = store

def security_agent(state):
    q = state["query"].strip()
    if len(q) > 4000:
        return {"answer": "Request is too long.", "requires_human_review": True}
    return {"query": q, "facts": [], "citations": [], "requires_human_review": False}

def supervisor_agent(state):
    q = state["query"].lower()
    intents = []
    if any(x in q for x in ["claim", "denied", "denial"]): intents.append("claim")
    if any(x in q for x in ["cover", "coverage", "benefit", "copay", "deductible"]): intents.append("benefits")
    if any(x in q for x in ["prior auth", "authorization", "authorisation"]): intents.append("prior_authorization")
    if any(x in q for x in ["policy", "rule", "document"]): intents.append("policy")
    if not intents: intents = ["policy"]
    return {"intents": list(dict.fromkeys(intents))}

def claims_agent(state):
    claim_id = state.get("claim_id")
    if not claim_id:
        match = re.search(r"\bCLM\d+\b", state["query"], re.I)
        claim_id = match.group(0).upper() if match else None
    if not claim_id:
        return {"facts": state["facts"] + ["No claim ID was supplied, so claim-specific status could not be retrieved."]}
    with SessionLocal() as db:
        claim = db.scalar(select(Claim).where(Claim.claim_id == claim_id, Claim.member_id == state["member_id"]))
    if not claim:
        fact = f"Claim {claim_id} was not found for this member."
    else:
        fact = f"Claim {claim.claim_id} for {claim.procedure} has status {claim.status}. Denial reason: {claim.denial_reason or 'None recorded'}."
    return {"facts": state["facts"] + [fact]}

def prior_auth_agent(state):
    with SessionLocal() as db:
        auth = db.scalar(select(PriorAuthorization).where(PriorAuthorization.member_id == state["member_id"], PriorAuthorization.procedure.ilike("%MRI%")))
    fact = f"Prior authorization status for MRI: {auth.status}." if auth else "No matching prior authorization record was found."
    return {"facts": state["facts"] + [fact]}

def rag_agent(state):
    docs = policy_store.search(state["query"], limit=3) if policy_store else []
    facts = state["facts"] + [d["text"] for d in docs]
    citations = state["citations"] + [{"policy_id": d["policy_id"], "section": d["section"], "page": d["page"]} for d in docs]
    return {"facts": facts, "citations": citations}

def response_agent(state):
    if not state.get("facts"):
        return {"answer": "I could not find enough information to answer that request.", "requires_human_review": True}
    return {"answer": generate_answer(state["query"], state["facts"])}
