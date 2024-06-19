from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema



class CategoryBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["This is my post"])]
    description: Annotated[str, Field(min_length=1, max_length=63206, examples=["This is the content of my post."])]

class Category(TimestampSchema, CategoryBase, PersistentDeletion):
    image: Annotated[str, Field(min_length=1, max_length=63206, examples=["This is the content of my post."])]
    created_by_user_id: int
    
    
class CategoryRead(BaseModel):
    id : int 
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["This is my post"])]
    description: Annotated[str, Field(min_length=1, max_length=63206, examples=["This is the content of my post."])]
    image: Annotated[str, Field(min_length=1, max_length=100000, examples=["This is the content of my post."])]
    created_by_user_id: int
    created_at: datetime

class CategoryCreate(CategoryBase):
    model_config = ConfigDict(extra="forbid")

    image: Annotated[str, Field(min_length=1, max_length=100000, examples=["This is the content of my post."])]



class CategoryCreateInternal(CategoryCreate):
    created_by_user_id: int
    description : str | None
    image : str | None = None


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[str | None, Field(min_length=2, max_length=30, examples=["This is my updated post"], default=None)]
    text: Annotated[
        str | None,
        Field(min_length=1, max_length=63206, examples=["This is the updated content of my post."], default=None),
    ]
    image: Annotated[str, Field(min_length=1, max_length=100000, examples=["This is the content of my post."])]


class CategoryUpdateInternal(CategoryUpdate):
    updated_at: datetime


class CategoryDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime

    