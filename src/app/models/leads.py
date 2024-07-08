from typing import List, Optional
from datetime import UTC, datetime
import uuid as uuid_pkg

from sqlalchemy import DateTime, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Mapped, mapped_column, relationship


from ..core.db.database import Base



class Leads(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(80))
    contact: Mapped[str] = mapped_column(String(80))
    place: Mapped[str] = mapped_column(String(30))
    price: Mapped[int] = mapped_column(Integer)
    franchise: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)

