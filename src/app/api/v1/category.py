from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from ...core.utils.cache import cache
from ...crud.crud_posts import crud_posts
from ...crud.crud_category import crud_category
from ...crud.crud_users import crud_users
from ...schemas.post import PostCreate, PostCreateInternal, PostRead, PostUpdate
from ...schemas.category import CategoryCreate, CategoryCreateInternal, CategoryRead, CategoryUpdate
from ...schemas.user import UserRead

router = APIRouter(tags=["category"])


@router.post("{username}/category", response_model=CategoryRead, status_code=201)
async def write_category(
    request: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> PostRead:
    db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username, is_deleted=False)
    if db_user is None:
        raise NotFoundException("User not found")

    category_internal_dict = {}
    image = form_data.get('image')
    form_data = await request.form()
    category_internal_dict['name'] = form_data.get('name')
    category_internal_dict['description'] = form_data.get('description')
    category_internal_dict["created_by_user_id"] = db_user["id"]

    category_internal = CategoryCreateInternal(**category_internal_dict)
    created_post: CategoryRead = await crud_posts.create(db=db, object=category_internal)
    return created_post


# @router.get("/{username}/posts", response_model=PaginatedListResponse[PostRead])
# @cache(
#     key_prefix="{username}_posts:page_{page}:items_per_page:{items_per_page}",
#     resource_id_name="username",
#     expiration=60,
# )
# async def read_posts(
#     request: Request,
#     username: str,
#     db: Annotated[AsyncSession, Depends(async_get_db)],
#     page: int = 1,
#     items_per_page: int = 10,
# ) -> dict:
#     db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username, is_deleted=False)
#     if not db_user:
#         raise NotFoundException("User not found")

#     posts_data = await crud_posts.get_multi(
#         db=db,
#         offset=compute_offset(page, items_per_page),
#         limit=items_per_page,
#         schema_to_select=PostRead,
#         created_by_user_id=db_user["id"],
#         is_deleted=False,
#     )

#     response: dict[str, Any] = paginated_response(crud_data=posts_data, page=page, items_per_page=items_per_page)
#     return response


# @router.get("/{username}/post/{id}", response_model=PostRead)
# @cache(key_prefix="{username}_post_cache", resource_id_name="id")
# async def read_post(
#     request: Request, username: str, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
# ) -> dict:
#     db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username, is_deleted=False)
#     if db_user is None:
#         raise NotFoundException("User not found")

#     db_post: PostRead | None = await crud_posts.get(
#         db=db, schema_to_select=PostRead, id=id, created_by_user_id=db_user["id"], is_deleted=False
#     )
#     if db_post is None:
#         raise NotFoundException("Post not found")

#     return db_post


# @router.patch("/{username}/post/{id}")
# @cache("{username}_post_cache", resource_id_name="id", pattern_to_invalidate_extra=["{username}_posts:*"])
# async def patch_post(
#     request: Request,
#     username: str,
#     id: int,
#     values: PostUpdate,
#     current_user: Annotated[UserRead, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(async_get_db)],
# ) -> dict[str, str]:
#     db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username, is_deleted=False)
#     if db_user is None:
#         raise NotFoundException("User not found")

#     if current_user["id"] != db_user["id"]:
#         raise ForbiddenException()

#     db_post = await crud_posts.get(db=db, schema_to_select=PostRead, id=id, is_deleted=False)
#     if db_post is None:
#         raise NotFoundException("Post not found")

#     await crud_posts.update(db=db, object=values, id=id)
#     return {"message": "Post updated"}


# @router.delete("/{username}/post/{id}")
# @cache("{username}_post_cache", resource_id_name="id", to_invalidate_extra={"{username}_posts": "{username}"})
# async def erase_post(
#     request: Request,
#     username: str,
#     id: int,
#     current_user: Annotated[UserRead, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(async_get_db)],
# ) -> dict[str, str]:
#     db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username, is_deleted=False)
#     if db_user is None:
#         raise NotFoundException("User not found")

#     if current_user["id"] != db_user["id"]:
#         raise ForbiddenException()

#     db_post = await crud_posts.get(db=db, schema_to_select=PostRead, id=id, is_deleted=False)
#     if db_post is None:
#         raise NotFoundException("Post not found")

#     await crud_posts.delete(db=db, id=id)

#     return {"message": "Post deleted"}


