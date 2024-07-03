from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession


from ...api.dependencies import  get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from ...core.utils.cache import cache
from ...core.schemas import ResponseSchema
from ...crud.crud_posts import crud_posts
from ...crud.crud_advertisement import crud_advertisement
from ...crud.crud_users import crud_users
from ...schemas.advertisement import AdvertisementCreate, AdvertisementCreateInternal, AdvertisementRead, AdvertisementUpdate
from ...schemas.user import UserRead
from ...service.external.s3_bucket import S3Utils

router = APIRouter(prefix='/user',tags=["users advertisement"])


@router.get("/advertisement", response_model=ResponseSchema)
async def get_categories(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:
    
    if current_user is None:
        raise NotFoundException("User not found")

    advertisement = await crud_advertisement.get_multi(db=db, created_by_user_id=current_user["id"])
    if not advertisement:
        raise NotFoundException(detail="Advertisement not found")

    return ResponseSchema(
        status_code= status.HTTP_200_OK,
        message="Advertisement successfully fetched",
        data=advertisement["data"]
    )

@router.get("/advertisement/{advertisement_id}", response_model=ResponseSchema)
async def get_advertisement(
    advertisement_id: int,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:
    
    if current_user is None:
        raise NotFoundException("User not found")

    advertisement = await crud_advertisement.get(db=db, id=advertisement_id)
    if not advertisement:
        raise NotFoundException("Advertisement not found")

    return ResponseSchema(
        status_code= status.HTTP_200_OK,
        message="Advertisement successfully fetched",
        data=advertisement
    )



@router.post("/advertisement", response_model=ResponseSchema, status_code=201)
async def write_advertisement(
    request: Request,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:
    
    if current_user is None:
        raise NotFoundException("User not found")

    advertisement_internal_dict = {}
    form_data = await request.form()
    image = form_data.get('image')
    advertisement_internal_dict['name'] = form_data.get('name','advertisement')
    advertisement_internal_dict['position'] = form_data.get('position',)
    advertisement_internal_dict["created_by_user_id"] = current_user["id"]

    s3_object = S3Utils()
    advertisements = []
    print(image,type(image))
    if image:
        image_url = s3_object.upload_image_to_s3(name=f"{current_user['uuid']}-{advertisement_internal_dict['name']}", file=image)
        advertisement_internal_dict["image"] = image_url
        advertisement_internal = AdvertisementCreateInternal(**advertisement_internal_dict)
        created_advertisement: AdvertisementRead = await crud_advertisement.create(db=db, object=advertisement_internal)
        advertisements.append(created_advertisement)
    return ResponseSchema(
        status_code= status.HTTP_201_CREATED,
        message="Advertisement successfully created",
        data=advertisements
    )

@router.patch("/advertisement/{advertisement_id}", response_model=ResponseSchema)
async def update_advertisement(
    advertisement_id: int,
    request: Request,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:

    if current_user is None:
        raise NotFoundException("User not found")
    advertisement = await crud_advertisement.get(db=db, id=advertisement_id)
    if not advertisement:
        raise NotFoundException("Advertisement not found")
    advertisement_update_dict = {}
    form_data = await request.form()
    image = form_data.get('image')
    advertisement_update_dict['name'] = form_data.get('name', 'advertisement')

    # Filter out keys with None values
    advertisement_update_dict = {k: v for k, v in advertisement_update_dict.items() if v is not None}


    s3_object = S3Utils()
    if image:
        image_url = s3_object.upload_image_to_s3(name=f"{current_user['uuid']}{advertisement['name']}", file=image)
        advertisement_update_dict["image_url"] = image_url
        s3_object.delete_image_from_s3(file_url=advertisement["image_url"])

    await crud_advertisement.update(db=db, object=advertisement_update_dict, id=advertisement["id"])
    updated_advertisement = await crud_advertisement.get(db=db, id=advertisement["id"])
  
    return ResponseSchema(
        status_code= status.HTTP_200_OK,
        message="Advertisement successfully updated",
        data=updated_advertisement
    )
  
@router.delete("/advertisement/{advertisement_id}", response_model=ResponseSchema)
async def delete_advertisement(
    advertisement_id: int,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:

    if current_user is None:
        raise NotFoundException("User not found")

    advertisement = await crud_advertisement.get(db=db, id=advertisement_id)
    if not advertisement:
        raise NotFoundException("Advertisement not found")

    await crud_advertisement.db_delete(db=db, id=advertisement_id)
    return ResponseSchema(
    status_code= status.HTTP_204_NO_CONTENT,
    message="Advertisement successfully deleted",
    data={}
)