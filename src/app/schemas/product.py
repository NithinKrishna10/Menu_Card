from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict

# Assuming PersistentDeletion, TimestampSchema, UUIDSchema are imported and defined similarly
from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema

class ProductBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["This is my product name"])]
    description: Annotated[str, Field(min_length=1, max_length=63206, examples=["This is the product description"])]
    price : int

class Product(TimestampSchema, ProductBase, PersistentDeletion):
    image: Optional[Annotated[str, Field(min_length=1, max_length=100000, examples=["This is the product image content."])]]
    created_by_user_id: int

class ProductRead(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["This is my product name"])]
    description: Annotated[str, Field(min_length=1, max_length=63206, examples=["This is the product description"])]
    image: Optional[Annotated[str, Field(min_length=1, max_length=100000, examples=["This is the product image content."])]]
    created_by_user_id: int
    created_at: datetime
    price : int
class ProductCreate(ProductBase):
    model_config = ConfigDict(extra="forbid")

    image: Optional[Annotated[str, Field(min_length=1, max_length=100000, examples=["This is the product image content."])]]

class ProductCreateInternal(ProductCreate):
    created_by_user_id: int
    image : str | None = None
    category_id : int
    description : str | None = None
    stock_available : bool = True
class ProductUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[Annotated[str, Field(min_length=2, max_length=30, examples=["This is my updated product name"], default=None)]]
    description: Optional[
        Annotated[
            str, 
            Field(min_length=1, max_length=63206, examples=["This is the updated product description"], default=None)
        ]
    ]
    image: Optional[Annotated[str, Field(min_length=1, max_length=100000, examples=["This is the updated product image content."])]] = None

class ProductUpdateInternal(BaseModel):
    image : str | None = None
    category_id : int | None = None
    description : str | None = None
    name : str |  None = None
    price : int | None = None
    stock_available : bool | None = None


class ProductDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
