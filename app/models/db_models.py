from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class Claim(Base):
    __tablename__ = "claims"
    claim_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    member_id: Mapped[str] = mapped_column(String(50), index=True)
    procedure: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30))
    denial_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    denial_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

class PriorAuthorization(Base):
    __tablename__ = "prior_authorizations"
    auth_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    member_id: Mapped[str] = mapped_column(String(50), index=True)
    procedure: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(String(100), index=True)
    query: Mapped[str] = mapped_column(Text)
    route: Mapped[str] = mapped_column(String(200))
    answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
