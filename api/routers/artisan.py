from datetime import datetime
from typing import Optional

import ormar
from fastapi import APIRouter
from fastapi_pagination.ext.ormar import paginate
from pydantic import BaseModel

from api import db
from api.models import user
from api.models.artisan import Artisan
from api.routers.pagination import DefaultPage
from api.routers.user import UserResponse


router = APIRouter()


class ArtisanResponse(BaseModel):
    id: int
    description: str
    image_url: Optional[str]
    name: str
    phone_no: Optional[str]
    age: Optional[int]
    user: UserResponse
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


@router.get("/artisans/", response_model=DefaultPage[ArtisanResponse])
async def list_artisans():
    return await paginate(
        Artisan.objects.select_all().order_by("-id"),
    )


@router.get("/artisans/{artisan_id}/", response_model=ArtisanResponse)
async def get_artisan(artisan_id: int):
    return await Artisan.objects.select_all().get(id=artisan_id)


class ArtisanCreateRequest(BaseModel):
    description: str
    image_url: Optional[str]
    name: str
    phone_no: Optional[str]
    age: Optional[int]
    user_id: int


@router.post("/artisans/", status_code=201, response_model=ArtisanResponse)
async def create_artisan(artisan: ArtisanCreateRequest):
    return await Artisan.objects.create(
        **artisan.model_dump(exclude={"user_id"}),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user=await user.User.objects.get(id=artisan.user_id),
    )


class ArtisanPatchRequest(BaseModel):
    description: Optional[str] = None
    image_url: Optional[str] = None
    name: Optional[str] = None
    phone_no: Optional[str] = None
    age: Optional[int] = None


class ArtisanPutRequest(BaseModel):
    description: str
    image_url: Optional[str]
    name: str
    phone_no: Optional[str]
    age: Optional[int]


@router.patch("/artisans/{artisan_id}/", response_model=ArtisanResponse)
@db.base_ormar_config.database.transaction()
async def patch_artisan(
    artisan_id: int,
    artisan: ArtisanPatchRequest,
):
    artisan_exists = await Artisan.objects.filter(pk=artisan_id).exists()
    if not artisan_exists:
        raise ormar.NoMatch()

    update_data = artisan.model_dump(exclude_unset=True)
    return await Artisan.objects.update_or_create(
        id=artisan_id,
        updated_at=datetime.now(),
        **update_data,
    )


@router.put("/artisans/{artisan_id}/", response_model=ArtisanResponse)
@db.base_ormar_config.database.transaction()
async def put_artisan(
    artisan_id: int,
    artisan: ArtisanPutRequest,
):
    artisan_exists = await Artisan.objects.filter(pk=artisan_id).exists()
    if not artisan_exists:
        raise ormar.NoMatch()

    return await Artisan.objects.update_or_create(
        id=artisan_id,
        updated_at=datetime.now(),
        **artisan.model_dump(),
    )


@router.delete("/artisans/{artisan_id}/", status_code=204)
async def delete_artisan(artisan_id: int) -> None:
    await Artisan.objects.delete(id=artisan_id)
