from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, status
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from ...core.security import blacklist_token, get_password_hash, oauth2_scheme
from ...core.schemas import ResponseSchema
from ...crud.crud_users import crud_users
from ...models.tier import Tier
from ...schemas.tier import TierRead
from ...schemas.user import UserCreate, UserCreateInternal, UserRead, UserUpdate
from ...service.external.s3_bucket import S3Utils
from ...service.utils.qr_code import generate_qr_code


router = APIRouter(tags=["users"])


@router.post("/user", response_model=ResponseSchema, status_code=201)
async def write_user(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> ResponseSchema:
    
    user_internal_dict = {}
    form_data = await request.form()
    image = form_data.get('image')
    user_internal_dict['name'] = form_data.get('name')
    user_internal_dict['username'] = form_data.get('username')
    user_internal_dict['email'] = form_data.get('email')
    user_internal_dict['password'] = form_data.get('password')
    
    email_row = await crud_users.exists(db=db, email=user_internal_dict['email'])
    if email_row:
        raise DuplicateValueException("Email is already registered")

    username_row = await crud_users.exists(db=db, username=user_internal_dict['username'])
    if username_row:
        raise DuplicateValueException("Username not available")
    s3_object = S3Utils() 
    if image:
        image_url = s3_object.upload_image_to_s3(name=user_internal_dict['name'], file=image)
        # qr_code = generate_qr_code(url="http://localhost:4200")
        # with open(qr_code, 'rb') as f:
        #     qr_code_url = s3_object.upload_image_to_s3(name=f"qr-{user_internal_dict['name']}", file=f) 
        #     user_internal_dict["qr_code"] = qr_code_url 
        user_internal_dict["image_url"] = image_url    
    user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
    del user_internal_dict["password"]

    user_internal = UserCreateInternal(**user_internal_dict)
    created_user: UserRead = await crud_users.create(db=db, object=user_internal)
    return ResponseSchema(
        status_code=status.HTTP_201_CREATED,
        message="user created",
        data=created_user
        
    )


@router.get("/users", response_model=PaginatedListResponse[UserRead])
async def read_users(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    users_data = await crud_users.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=UserRead,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/user/me/", response_model=UserRead)
async def read_users_me(request: Request, current_user: Annotated[UserRead, Depends(get_current_user)]) -> UserRead:
    return current_user


@router.get("/user/{username}", response_model=UserRead)
async def read_user(request: Request, username: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict:
    db_user: UserRead | None = await crud_users.get(
        db=db, schema_to_select=UserRead, username=username, is_deleted=False
    )
    if db_user is None:
        raise NotFoundException("User not found")

    return db_user

@router.patch("/user", response_model=UserRead)
async def update_user(
    # user_id: int, 
    request: Request, 
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> UserRead | None:
    print(current_user)
    user_update_dict = {}
    form_data = await request.form()
    image = form_data.get('image')
    user_update_dict['name'] = form_data.get('name')
    user_update_dict['username'] = form_data.get('username')
    user_update_dict['email'] = form_data.get('email')
    # user_update_dict['password'] = form_data.get('password')

    # current_user = await crud_users.get(db=db, id=user_id)
    if not current_user:
        raise NotFoundException("User not found")

    if user_update_dict.get('email') and user_update_dict['email'] != current_user["email"]:
        email_row = await crud_users.exists(db=db, email=user_update_dict['email'])
        if email_row:
            raise DuplicateValueException("Email is already registered")

    if user_update_dict.get('username') and user_update_dict['username'] != current_user["username"]:
        username_row = await crud_users.exists(db=db, username=user_update_dict['username'])
        if username_row:
            raise DuplicateValueException("Username not available")

    s3_object = S3Utils()
    if image:
        image_url = s3_object.upload_image_to_s3(name=user_update_dict['name'], file=image)
        user_update_dict["image_url"] = image_url
        s3_object.delete_image_from_s3(file_url=current_user["image_url"])

    # if user_update_dict.get('password'):
    #     user_update_dict["hashed_password"] = get_password_hash(password=user_update_dict["password"])
    #     del user_update_dict["password"]
    user_update_dict = {k: v for k, v in user_update_dict.items() if v is not None}
    await crud_users.update(db=db, object=user_update_dict, id=current_user["id"])
    updated_user = await crud_users.get(db=db, id=current_user["id"])
    return updated_user

@router.delete("/user")
async def erase_user(
    request: Request,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    db_user = await crud_users.get(db=db, schema_to_select=UserRead, id=current_user["id"])
    if not db_user:
        raise NotFoundException("User not found")


    await crud_users.delete(db=db, id=current_user["id"])
    await blacklist_token(token=token, db=db)
    return {"message": "User deleted"}


@router.delete("/db_user", dependencies=[Depends(get_current_superuser)])
async def erase_db_user(
    request: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    db_user = await crud_users.exists(db=db, username=username)
    if not db_user:
        raise NotFoundException("User not found")

    await crud_users.db_delete(db=db, username=username)
    await blacklist_token(token=token, db=db)
    return {"message": "User deleted from the database"}

