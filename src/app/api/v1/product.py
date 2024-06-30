import json
from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, Request, status
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession


from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from ...core.utils.cache import cache
from ...core.schemas import ResponseSchema
from ...crud.crud_products import crud_product, crud_product_portion
from ...crud.crud_category import crud_category
from ...crud.crud_users import crud_users
from ...schemas.post import PostCreate, PostCreateInternal, PostRead, PostUpdate
from ...schemas.category import CategoryCreate, CategoryCreateInternal, CategoryRead, CategoryUpdate
from ...schemas.product import ProductRead, ProductCreate, ProductCreateInternal, ProductUpdateInternal, ProductPortionCreate, ProductPortionUpdate, ProductPortionCreateInternal
from ...schemas.user import UserRead
from ...service.external.s3_bucket import S3Utils
from ...models.product import ProductPortion, Product


router = APIRouter(prefix="/user", tags=["users products"])


@router.get("/product", response_model=ResponseSchema)
async def get_product(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:

    if current_user is None:
        raise NotFoundException("User not found")

    # product = await crud_product.get_multi_joined(db=db, created_by_user_id=current_user["id"],join_model=ProductPortion,join_on=ProductPortion.product_id==Product.id)
    # join_condition = (  == )
    join_condition = ProductPortion.product_id == Product.id
    # Perform the joined query
    product = await crud_product.get_multi_joined(
        db=db,
        join_on=ProductPortion.product_id == Product.id,
        join_model=ProductPortion,
        join_schema_to_select=ProductRead,
        nest_joins = True,
        relationship_type='one-to-many',
        created_by_user_id=current_user["id"],
    )
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

    # product = await crud_product.get(db=db, created_by_user_id=current_user["id"], id=product_id,schema_to_select=ProductRead)
    product = await crud_product.get_joined(
        db=db,
        join_on=ProductPortion.product_id == Product.id,
        join_model=ProductPortion,
        join_schema_to_select=ProductRead,
        nest_joins=True,
        relationship_type='one-to-many',
        created_by_user_id=current_user["id"],
        id=product_id
    )
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
    print(form_data)
    image = form_data.get('image')
    product_internal_dict['name'] = form_data.get('name')
    product_internal_dict['stock_available'] = form_data.get('stock_available')
    product_internal_dict['price'] = form_data.get('price',0)
    product_internal_dict['portion'] = form_data.get('portion')
    category_id = int(form_data.get('category_id',1))
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
    if created_product.portion:
        portions = form_data.get('portions') 
        portions_list = json.loads(portions)  # Parse JSON string into a list of dictionaries

        for portion in portions_list:
            portion_object = ProductPortionCreateInternal(
                name=portion["name"],
                price=portion["price"],
                stock_available=portion["stock_available"],
                product_id = created_product.id
            )
            await crud_product_portion.create(db=db, object=portion_object)
    product: ProductRead = await crud_product.get(db=db,id= created_product.id, schema_to_select=ProductRead)
    product["portions"]=await crud_product_portion.get_multi(db=db, product_id= product["id"])
    return ResponseSchema(
        status_code= status.HTTP_201_CREATED,
        message="Product successfully created",
        data=product
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
    
    portions = form_data.get('portions')
    portions_list = json.loads(portions) 

    for portion in portions_list:
        
        p_t = await crud_product_portion.get(db=db, product_id=product_id, name=portion["name"])
        if p_t:
            await crud_product_portion.update(db=db, object={"price":p_t["price"]}, id=p_t["id"])
        else:      
            portion_object = ProductPortionCreateInternal(
                name=portion["name"],
                price=portion["price"],
                stock_available=portion["stock_available"],
                product_id = product_id
            )
            await crud_product_portion.create(db=db, object=portion_object)
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



@router.get("/productportion/{product_portion_id}", response_model=ResponseSchema)
def read_product_portion(product_portion_id: int, current_user: Annotated[UserRead, Depends(get_current_user)], db: AsyncSession = Depends(async_get_db)):
    db_product_portion = crud_product_portion.get(db=db, id=product_portion_id)
    if db_product_portion is None:
        raise NotFoundException("Product portion not found")
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        message="Product Portion successfully deleted",
        data=db_product_portion
    )


@router.post("/productportion/{product_id}", response_model=ProductPortion)
async def write_product_portion(product_portion_id: int, product_portion: ProductPortionCreate, current_user: Annotated[UserRead, Depends(get_current_user)], db: AsyncSession = Depends(async_get_db)):
    db_product = crud_product.get(db=db, id=product_portion_id, created_by_user_id=current_user["id"])
    if db_product is None:
        raise NotFoundException("Product not found")
    
    obj_in = ProductPortionCreateInternal(
        name=product_portion.name,
        stock_available=product_portion.stock_available,
        price=product_portion.price,
        product_id=db_product["id"]
    )
    db_product_portion = await crud_product_portion.create(db=db, object=product_portion)
    if db_product_portion is None:
        raise NotFoundException("Product portion not found")
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        message="Product Portion successfully updated",
        data=db_product_portion
    )

@router.patch("/productportion/{product_portion_id}", response_model=ResponseSchema)
async def update_product_portion(product_portion_id: int, product_portion: ProductPortionUpdate, current_user: Annotated[UserRead, Depends(get_current_user)], db: AsyncSession = Depends(async_get_db)):
    db_product_portion = await crud_product_portion.get(db=db, id=product_portion_id)
    product_portion = product_portion.model_dump()
    product_portion = {k: v for k,v in product_portion.items() if v is not None}
    if db_product_portion is None:
        raise NotFoundException("Product portion not found")
    await crud_product_portion.update(db=db, object=product_portion, id=product_portion_id)
    db_product_portion = await crud_product_portion.get(db=db, id=product_portion_id)
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        message="Product Portion successfully updated",
        data=db_product_portion     
    )


@router.delete("/productportion/{product_portion_id}", response_model=ResponseSchema)
async def delete_product_portion(product_portion_id: int, current_user: Annotated[UserRead, Depends(get_current_user)], db: AsyncSession = Depends(async_get_db)):
    db_product_portion = await crud_product_portion.get(db=db, id=product_portion_id)
    if db_product_portion is None:
        raise NotFoundException("Product portion not found")
    db_product_portions = await crud_product_portion.get_multi(db=db, product_id=db_product_portion["product_id"])
    if len(db_product_portions["data"]) >2:
        await crud_product_portion.delete(db=db, id=product_portion_id)
    else:
        for portions in db_product_portions["data"]:
            print(portions)
            await crud_product_portion.delete(db=db, id=portions["id"])
        return ResponseSchema(
        status_code=status.HTTP_204_NO_CONTENT,
        message="Product Portion successfully deleted",
        data={}
    )
        
    
    if db_product_portion is None:
        raise NotFoundException("Product portion not found")
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        message="Product Portion successfully deleted",
        data={}
    )

@router.get("/productportions/", response_model=list[ProductPortion])
async def read_product_portions( current_user: Annotated[UserRead, Depends(get_current_user)], db: AsyncSession = Depends(async_get_db)):
    product_portions = await crud_product_portion.get_multi(db=db)
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        message="Product Portion successfully fetched",
        data=product_portions
    )
