from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, Request, status
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession


from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from ...core.utils.cache import cache
from ...core.schemas import ResponseSchema
from ...crud.crud_posts import crud_posts
from ...crud.crud_category import crud_category
from ...crud.crud_products import crud_product
from ...crud.crud_users import crud_users
from ...schemas.post import PostCreate, PostCreateInternal, PostRead, PostUpdate
from ...schemas.category import CategoryCreate, CategoryCreateInternal, CategoryRead, CategoryUpdate
from ...schemas.user import UserRead
from ...service.external.s3_bucket import S3Utils

router = APIRouter(tags=["Menu Card"])


@router.get("/category", response_model=ResponseSchema)
async def get_categories(
    user_id: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:
    current_user = await crud_users.get(db=db, uuid = user_id)
    if current_user is None:
        raise NotFoundException("User not found")

    category = await crud_category.get_multi(db=db, created_by_user_id=current_user["id"])
    if not category:
        raise NotFoundException(detail="Category not found")

    return ResponseSchema(
        status_code= status.HTTP_200_OK,
        message="Category successfully fetched",
        data=category["data"]
    )

@router.get("/category/{category_id}", response_model=ResponseSchema)
async def get_category(
    category_id: int,
    user_id: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:
    
    current_user = await crud_users.get(db=db, uuid = user_id)
    if current_user is None:
        raise NotFoundException("User not found")

    category = await crud_category.get(db=db, id=category_id)
    if not category:
        raise NotFoundException("Category not found")

    return ResponseSchema(
        status_code= status.HTTP_200_OK,
        message="Category successfully fetched",
        data=category
    )



@router.get("/product", response_model=ResponseSchema)
async def get_product(
    user_id: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    category_id : int = None
) -> ResponseSchema:
    
    current_user = await crud_users.get(db=db, uuid = user_id)
    if current_user is None:
        raise NotFoundException("User not found")
    if category_id:
        product = await crud_product.get_multi(db=db, created_by_user_id=current_user["id"],category_id=category_id)
    else:
        product = await crud_product.get_multi(db=db, created_by_user_id=current_user["id"])
    if not product:
        raise NotFoundException("Product not found")
    return ResponseSchema(
        status_code= status.HTTP_200_OK,
        message="Product successfully fetched",
        data=product["data"]
    )


@router.get("/product/{product_id}", response_model=ResponseSchema)
async def get_product(
    product_id: int,
    user_id: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:
    current_user = await crud_users.get(db=db, uuid = user_id)
    if current_user is None:
        raise NotFoundException("User not found")

    product = await crud_product.get(db=db, created_by_user_id=current_user["id"], id=product_id)
    if not product:
        raise NotFoundException("Product not found")
    return ResponseSchema(
        status_code= status.HTTP_200_OK,
        message="Product successfully fetched",
        data=product
    )