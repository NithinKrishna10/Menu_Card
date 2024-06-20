from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, Request, status
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession


from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from ...core.utils.cache import cache
from ...core.schemas import ResponseSchema
from ...crud.crud_products import crud_product
from ...crud.crud_category import crud_category
from ...crud.crud_users import crud_users
from ...schemas.post import PostCreate, PostCreateInternal, PostRead, PostUpdate
from ...schemas.category import CategoryCreate, CategoryCreateInternal, CategoryRead, CategoryUpdate
from ...schemas.product import ProductRead, ProductCreate, ProductCreateInternal, ProductUpdateInternal, ProductUpdate
from ...schemas.user import UserRead
from ...service.external.s3_bucket import S3Utils

router = APIRouter(prefix="/user", tags=["users products"])


@router.get("/product", response_model=ResponseSchema)
async def get_product(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:

    if current_user is None:
        raise NotFoundException("User not found")

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
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:

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

@router.post("/product", response_model=ResponseSchema, status_code=201)
async def write_product(
    request: Request,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:

    if current_user is None:
        raise NotFoundException("User not found")

    product_internal_dict = {}
    form_data = await request.form()
    image = form_data.get('image')
    product_internal_dict['name'] = form_data.get('name')
    product_internal_dict['stock_available'] = form_data.get('stock_available')
    product_internal_dict['price'] = form_data.get('price')
    category_id = int(form_data.get('category_id'))
    category = await crud_category.get(db=db, id=category_id, created_by_user_id=current_user["id"])
    if category is None:
        raise NotFoundException("Category not found")
    product_internal_dict['category_id'] = category_id
    product_internal_dict['description'] = form_data.get('description')
    product_internal_dict["created_by_user_id"] = current_user["id"]
    s3_object = S3Utils()
    if image:
        image_url = s3_object.upload_image_to_s3(name=product_internal_dict['name'], file=image)
        product_internal_dict["image"] = image_url
    product_internal = ProductCreateInternal(**product_internal_dict)
    created_product: ProductRead = await crud_product.create(db=db, object=product_internal)
    return ResponseSchema(
        status_code= status.HTTP_201_CREATED,
        message="Product successfully created",
        data=created_product
    )



@router.patch("/product/{product_id}", response_model=ResponseSchema)
async def update_product(
    product_id: int,
    request: Request,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:

    if current_user is None:
        raise NotFoundException("User not found")
    product = await crud_product.get(db=db, id=product_id)
    if not product:
        raise NotFoundException("Product not found")

    product_update_dict = {}
    form_data = await request.form()
    image = form_data.get('image')
    product_update_dict['name'] = form_data.get('name')
    product_update_dict['price'] = form_data.get('price')
    product_update_dict['stock_available'] = form_data.get('stock_available')
    product_update_dict['description'] = form_data.get('description')
    category_id = form_data.get('category_id')
    if category_id:
        category = await crud_category.get(db=db, id=int(category_id), created_by_user_id=current_user["id"])
        if category is None:
            raise NotFoundException("Category not found")



    s3_object = S3Utils()
    if image:
        image_url = s3_object.upload_image_to_s3(
            name=product_update_dict['name'], file=image)
        product_update_dict["image"] = image_url
        s3_object.delete_image_from_s3(file_url=product["image"])
    product_update_dict['category_id'] = category_id
    product_obj = ProductUpdateInternal(**product_update_dict)
    product_update_dict = product_obj.model_dump(exclude_unset=True)
    # Filter out keys with None values
    product_update_dict = {k: v for k,v in product_update_dict.items() if v is not None}
    await crud_product.update(db=db, object=product_update_dict, id=product_id)
    updated_product = await crud_product.get(db=db, id=product_id)
    
    
    return ResponseSchema(
        status_code= status.HTTP_200_OK,
        message="Product successfully updated",
        data=updated_product
    )

@router.delete("/product/{product_id}", response_model=ResponseSchema)
async def delete_product(
    product_id: int,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:

    if current_user is None:
        raise NotFoundException("User not found")

    product = await crud_product.get(db=db, id=product_id)
    if not product:
        raise NotFoundException("Product not found")

    await crud_product.db_delete(db=db, id=product_id)
    
    return ResponseSchema(
    status_code= status.HTTP_204_NO_CONTENT,
    message="Product successfully deleted",
    data={}
)
