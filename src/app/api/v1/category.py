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
from ...crud.crud_users import crud_users
from ...schemas.post import PostCreate, PostCreateInternal, PostRead, PostUpdate
from ...schemas.category import CategoryCreate, CategoryCreateInternal, CategoryRead, CategoryUpdate
from ...schemas.user import UserRead
from ...service.external.s3_bucket import S3Utils

router = APIRouter(prefix='/user',tags=["users category"])


@router.get("/category", response_model=ResponseSchema)
async def get_categories(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:
    
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
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:
    
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



@router.post("/category", response_model=ResponseSchema, status_code=201)
async def write_category(
    request: Request,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:
    
    # if current_user is None:
    #     raise NotFoundException("User not found")

    category_internal_dict = {}
    form_data = await request.form()
    image = form_data.get('image')
    category_internal_dict['name'] = form_data.get('name')
    category_internal_dict['description'] = form_data.get('description')
    category_internal_dict["created_by_user_id"] = current_user["id"]

    s3_object = S3Utils()
    if image:
        image_url = s3_object.upload_image_to_s3(name=f"{current_user["uuid"]}-{category_internal_dict['name']}", file=image)
        category_internal_dict["image"] = image_url
    category_internal = CategoryCreateInternal(**category_internal_dict)
    created_category: CategoryRead = await crud_category.create(db=db, object=category_internal)
    
    return ResponseSchema(
        status_code= status.HTTP_201_CREATED,
        message="Category successfully created",
        data=created_category
    )

@router.patch("/category/{category_id}", response_model=ResponseSchema)
async def update_category(
    category_id: int,
    request: Request,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:

    if current_user is None:
        raise NotFoundException("User not found")
    category = await crud_category.get(db=db, id=category_id)
    if not category:
        raise NotFoundException("Category not found")
    category_update_dict = {}
    form_data = await request.form()
    image = form_data.get('image')
    category_update_dict['name'] = form_data.get('name')
    category_update_dict['description'] = form_data.get('description')

    # Filter out keys with None values
    category_update_dict = {k: v for k, v in category_update_dict.items() if v is not None}


    s3_object = S3Utils()
    if image:
        image_url = s3_object.upload_image_to_s3(name=f"{current_user["uuid"]}{category['name']}", file=image)
        category_update_dict["image_url"] = image_url
        s3_object.delete_image_from_s3(file_url=category["image_url"])

    await crud_category.update(db=db, object=category_update_dict, id=category["id"])
    updated_category = await crud_category.get(db=db, id=category["id"])
  
    return ResponseSchema(
        status_code= status.HTTP_200_OK,
        message="Category successfully updated",
        data=updated_category
    )
  
@router.delete("/category/{category_id}", response_model=ResponseSchema)
async def delete_category(
    category_id: int,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:

    if current_user is None:
        raise NotFoundException("User not found")

    category = await crud_category.get(db=db, id=category_id)
    if not category:
        raise NotFoundException("Category not found")

    await crud_category.db_delete(db=db, id=category_id)
    return ResponseSchema(
    status_code= status.HTTP_204_NO_CONTENT,
    message="Category successfully deleted",
    data={}
)