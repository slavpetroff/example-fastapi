from datetime import datetime
from typing import Optional

import ormar
from fastapi import APIRouter
from fastapi_pagination.ext.ormar import paginate
from pydantic import BaseModel

from api import db
from api.models.artisan import Artisan
from api.models.item import Item
from api.models.tag import Tag
from api.routers.artisan import ArtisanResponse
from api.routers.pagination import DefaultPage


router = APIRouter()


class TagResponse(BaseModel):
    id: int
    name: str
    item: Item
    created_by: ArtisanResponse
    created_at: datetime
    updated_at: datetime


@router.get("/tags/", response_model=DefaultPage[TagResponse])
async def list_tags():
    return await paginate(Tag.objects.select_all().order_by("-id"))


@router.get("/tags/{tag_id}/", response_model=TagResponse)
async def get_tag(tag_id: int):
    return await Tag.objects.select_all().get(id=tag_id)


class TagCreateRequest(BaseModel):
    name: str
    item_id: int
    created_by_id: int


@router.post("/tags/", status_code=201, response_model=TagResponse)
async def create_tag(tag: TagCreateRequest):
    # Fetch the related models
    item = await Item.objects.get(id=tag.item_id)
    created_by = await Artisan.objects.get(id=tag.created_by_id)

    return await Tag.objects.create(
        **tag.model_dump(exclude={"item_id", "created_by_id"}),
        item=item,
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


class TagPatchRequest(BaseModel):
    name: Optional[str] = None


class TagPutRequest(BaseModel):
    name: str


@router.patch("/tags/{tag_id}/", response_model=TagResponse)
@db.base_ormar_config.database.transaction()
async def patch_tag(tag_id: int, tag: TagPatchRequest):
    tag_exists = await Tag.objects.filter(pk=tag_id).exists()
    if not tag_exists:
        raise ormar.NoMatch()

    update_data = tag.model_dump(exclude_unset=True)
    return await Tag.objects.update_or_create(
        id=tag_id,
        updated_at=datetime.now(),
        **update_data,
    )


@router.put("/tags/{tag_id}/", response_model=TagResponse)
@db.base_ormar_config.database.transaction()
async def put_tag(tag_id: int, tag: TagPutRequest):
    tag_exists = await Tag.objects.filter(pk=tag_id).exists()
    if not tag_exists:
        raise ormar.NoMatch()

    return await Tag.objects.update_or_create(
        id=tag_id,
        updated_at=datetime.now(),
        **tag.model_dump(),
    )


@router.delete("/tags/{tag_id}/", status_code=204)
async def delete_tag(tag_id: int) -> None:
    await Tag.objects.delete(id=tag_id)
