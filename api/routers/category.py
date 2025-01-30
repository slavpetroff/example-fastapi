from datetime import datetime
from typing import Optional

import ormar
from fastapi import APIRouter
from fastapi_pagination.ext.ormar import paginate
from pydantic import BaseModel

from api import db
from api.models.category import Category
from api.routers.pagination import DefaultPage


router = APIRouter()


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


@router.get("/categories/", response_model=DefaultPage[CategoryResponse])
async def list_categories():
    return await paginate(
        Category.objects.select_all().order_by("-id"),
    )


@router.get("/categories/{category_id}/", response_model=CategoryResponse)
async def get_category(category_id: int):
    return await Category.objects.get(id=category_id)


class CategoryCreateRequest(BaseModel):
    name: str
    description: str


@router.post("/categories/", status_code=201, response_model=CategoryResponse)
async def create_category(category: CategoryCreateRequest):
    return await Category.objects.create(
        **category.model_dump(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


class CategoryPatchRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryPutRequest(BaseModel):
    name: str
    description: str


@router.patch("/categories/{category_id}/", response_model=CategoryResponse)
@db.base_ormar_config.database.transaction()
async def patch_category(
    category_id: int,
    category: CategoryPatchRequest,
):
    # Assert that the category exists
    category_exists = await Category.objects.filter(pk=category_id).exists()
    if not category_exists:
        raise ormar.NoMatch()

    # Update only provided fields
    update_data = category.model_dump(exclude_unset=True)
    return await Category.objects.update_or_create(
        id=category_id,
        updated_at=datetime.now(),
        **update_data,
    )


@router.put("/categories/{category_id}/", response_model=CategoryResponse)
@db.base_ormar_config.database.transaction()
async def put_category(
    category_id: int,
    category: CategoryPutRequest,
):
    # Assert that the category exists
    category_exists = await Category.objects.filter(pk=category_id).exists()
    if not category_exists:
        raise ormar.NoMatch()

    # Full replacement of the resource
    return await Category.objects.update_or_create(
        id=category_id,
        updated_at=datetime.now(),
        **category.model_dump(),
    )


@router.delete("/categories/{category_id}/", status_code=204)
async def delete_category(category_id: int) -> None:
    await Category.objects.delete(id=category_id)
