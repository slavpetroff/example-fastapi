from datetime import datetime
from typing import Optional

import ormar
from fastapi import APIRouter
from fastapi_pagination.ext.ormar import paginate
from pydantic import BaseModel

from api import db
from api.models.artisan import Artisan
from api.models.category import Category
from api.models.item import Item
from api.routers.artisan import ArtisanResponse
from api.routers.category import CategoryResponse
from api.routers.pagination import DefaultPage


router = APIRouter()


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    published: bool
    price: int
    created_at: datetime
    updated_at: datetime
    creator: ArtisanResponse
    categories: list[CategoryResponse]


@router.get("/items/", response_model=DefaultPage[ItemResponse])
async def list_items():
    return await paginate(
        Item.objects.select_all().order_by("-id"),
    )


@router.get("/items/{item_id}/", response_model=ItemResponse)
async def get_item(item_id: int):
    return await Item.objects.filter(id=item_id).select_all().first()


class ItemCreateRequest(BaseModel):
    name: str
    description: str
    published: bool = False
    price: int
    creator_id: int
    category_ids: list[int]


@router.post("/items/", status_code=201, response_model=ItemResponse)
async def create_item(item: ItemCreateRequest):
    return await Item.objects.create(
        **item.model_dump(exclude={"creator_id", "category_ids"}),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        creator=await Artisan.objects.get(id=item.creator_id),
        categories=await Category.objects.filter(
            id__in=item.category_ids,
        ).all(),
    )


class ItemPatchRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    published: Optional[bool] = None
    price: Optional[int] = None
    creator_id: Optional[int] = None
    category_ids: Optional[list[int]] = None


@router.patch("/items/{item_id}/", response_model=ItemResponse)
async def patch_item(item_id: int, item: ItemPatchRequest):
    # Check if the item exists
    async with db.database.transaction():
        item_exists = await Item.objects.filter(pk=item_id).exists()
        if not item_exists:
            raise ormar.NoMatch()

        # Prepare the update data
        update_data = item.model_dump(exclude={"creator_id", "category_ids"})

        # Handle creator_id if provided
        if item.creator_id is not None:
            creator_exists = await Artisan.objects.filter(
                id=item.creator_id,
            ).exists()
            if not creator_exists:
                raise ValueError("Creator does not exist.")  # noqa: TRY003
            update_data["creator"] = await Artisan.objects.get(
                id=item.creator_id,
            )

        # Handle category_ids if provided
        if item.category_ids is not None:
            categories = await Category.objects.filter(
                id__in=item.category_ids,
            ).all()
            if len(categories) != len(item.category_ids):
                raise ValueError(  # noqa: TRY003
                    "One or more categories do not exist.",
                )
            update_data["categories"] = categories

        # Update the item
        return await Item.objects.update_or_create(
            id=item_id,
            updated_at=datetime.now(),
            **update_data,
        )


class ItemPutRequest(BaseModel):
    name: str
    description: str
    published: bool
    price: int
    creator_id: int
    category_ids: list[int]


@router.put("/items/{item_id}/", response_model=ItemResponse)
@db.base_ormar_config.database.transaction()
async def put_item(item_id: int, item: ItemPutRequest):
    item_exists = await Item.objects.filter(pk=item_id).exists()
    if not item_exists:
        raise ormar.NoMatch()

    return await Item.objects.update_or_create(
        id=item_id,
        updated_at=datetime.now(),
        **item.model_dump(),
    )


@router.delete("/items/{item_id}/", status_code=204)
async def delete_item(item_id: int) -> None:
    await Item.objects.delete(id=item_id)
