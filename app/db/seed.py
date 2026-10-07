from sqlalchemy import select
from app.db.database import Base, engine, SessionLocal
from app.models.db_models import Claim, PriorAuthorization

def init_and_seed():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.scalar(select(Claim).where(Claim.claim_id == "CLM123")):
            db.add(Claim(claim_id="CLM123", member_id="MEM001", procedure="MRI", status="DENIED", denial_code="AUTH_REQUIRED", denial_reason="Required prior authorization was not obtained."))
        if not db.scalar(select(PriorAuthorization).where(PriorAuthorization.auth_id == "PA100")):
            db.add(PriorAuthorization(auth_id="PA100", member_id="MEM001", procedure="MRI", status="NOT_FOUND"))
        db.commit()
