from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, Request, status
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from ...core.utils.cache import cache
from ...core.schemas import ResponseSchema
from ...crud.crud_posts import crud_posts
from ...crud.crud_leads import crud_leads
from ...crud.crud_leads import crud_leads
from ...crud.crud_users import crud_users
from ...schemas.leads import LeadsCreate, LeadsRead
from ...schemas.user import UserRead
from ...service.external.s3_bucket import S3Utils

router = APIRouter(prefix='/user',tags=["users leads"])


@router.get("/leads", response_model=ResponseSchema)
async def get_leadses(
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:
    

    leads = await crud_leads.get_multi(db=db)
    if not leads:
        raise NotFoundException(detail="Leads not found")

    return ResponseSchema(
        status_code= status.HTTP_200_OK,
        message="Leads successfully fetched",
        data=leads["data"]
    )

@router.get("/leads/{leads_id}", response_model=ResponseSchema)
async def get_leads(
    leads_id: int,
    # current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:


    leads = await crud_leads.get(db=db, id=leads_id)
    if not leads:
        raise NotFoundException("Leads not found")

    return ResponseSchema(
        status_code= status.HTTP_200_OK,
        message="Leads successfully fetched",
        data=leads
    )



@router.post("/leads", response_model=ResponseSchema, status_code=201)
async def write_leads(
    request: Request,
    leads : LeadsCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:
    


    created_leads: LeadsRead = await crud_leads.create(db=db, object=leads)
    
    return ResponseSchema(
        status_code= status.HTTP_201_CREATED,
        message="Leads successfully created",
        data=created_leads
    )

# @router.patch("/leads/{leads_id}", response_model=ResponseSchema)
# async def update_leads(
#     leads_id: int,
#     request: Request,
#     current_user: Annotated[UserRead, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(async_get_db)],
# ) -> ResponseSchema:

   
  
#     return ResponseSchema(
#         status_code= status.HTTP_200_OK,
#         message="Leads successfully updated",
#         data=updated_leads
#     )
  
@router.delete("/leads/{leads_id}", response_model=ResponseSchema)
async def delete_leads(
    leads_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ResponseSchema:


    leads = await crud_leads.get(db=db, id=leads_id)
    if not leads:
        raise NotFoundException("Leads not found")

    await crud_leads.db_delete(db=db, id=leads_id)
    return ResponseSchema(
        status_code=status.HTTP_204_NO_CONTENT,
        message="Leads successfully deleted",
        data={}
    )
