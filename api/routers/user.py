from datetime import datetime
from typing import Optional

import ormar
from fastapi import APIRouter
from fastapi_pagination.ext.ormar import paginate
from pydantic import BaseModel

from api import db
from api.models.user import User
from api.routers.pagination import DefaultPage


router = APIRouter()


class UserResponse(BaseModel):
    id: int
    email: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]


@router.get("/users/", response_model=DefaultPage[UserResponse])
async def list_users():
    return await paginate(User.objects.select_all().order_by("-id"))


@router.get("/users/{user_id}/", response_model=UserResponse)
async def get_user(user_id: int):
    return await User.objects.get(id=user_id)


class UserCreateRequest(BaseModel):
    email: str
    password: str


@router.post("/users/", status_code=201, response_model=UserResponse)
async def create_user(user: UserCreateRequest):
    return await User.objects.create(
        **user.model_dump(),
        created_at=datetime.now(),
    )


class UserPatchRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class UserPutRequest(BaseModel):
    name: str
    email: str


@router.patch("/users/{user_id}/", response_model=UserResponse)
@db.base_ormar_config.database.transaction()
async def patch_user(user_id: int, user: UserPatchRequest):
    user_exists = await User.objects.filter(pk=user_id).exists()
    if not user_exists:
        raise ormar.NoMatch()

    update_data = user.model_dump(exclude_unset=True)
    return await User.objects.update_or_create(
        id=user_id,
        updated_at=datetime.now(),
        **update_data,
    )


@router.put("/users/{user_id}/", response_model=UserResponse)
@db.base_ormar_config.database.transaction()
async def put_user(user_id: int, user: UserPutRequest):
    user_exists = await User.objects.filter(pk=user_id).exists()
    if not user_exists:
        raise ormar.NoMatch()

    return await User.objects.update_or_create(
        id=user_id,
        updated_at=datetime.now(),
        **user.model_dump(),
    )


@router.delete("/users/{user_id}/", status_code=204)
async def delete_user(user_id: int) -> None:
    await User.objects.delete(id=user_id)
