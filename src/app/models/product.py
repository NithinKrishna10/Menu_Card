from typing import List, Optional
from datetime import UTC, datetime
import uuid as uuid_pkg

from sqlalchemy import DateTime, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Mapped, mapped_column, relationship


from ..core.db.database import Base


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"), index=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(63206),nullable=True)
    price: Mapped[int] = mapped_column(Integer)
    image: Mapped[str | None] = mapped_column(String, default=None)
    stock_available: Mapped[bool] = mapped_column(default=True)
    portion: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)

    portions = relationship("ProductPortion", back_populates="product", lazy="selectin")

class ProductPortion(Base):
    __tablename__ = "product_portion"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    name: Mapped[str] = mapped_column(String(30))
    price: Mapped[int] = mapped_column(Integer)
    stock_available: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)

    product = relationship("Product", back_populates="portions")