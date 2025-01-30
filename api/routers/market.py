from datetime import datetime
from typing import Optional

import ormar
from fastapi import APIRouter
from fastapi_pagination.ext.ormar import paginate
from pydantic import BaseModel

from api import db, get_logger
from api.models.artisan import Artisan
from api.models.market import Market
from api.routers.artisan import ArtisanResponse
from api.routers.pagination import DefaultPage


router = APIRouter()
logger = get_logger(__name__)


class MarketResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    city: str
    country: str
    description: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    owner: ArtisanResponse
    maintainers: list[ArtisanResponse]


@router.get("/markets/", response_model=DefaultPage[MarketResponse])
async def list_markets():
    return await paginate(Market.objects.select_all().order_by("-id"))


@router.get("/markets/{market_id}/", response_model=MarketResponse)
async def get_market(market_id: int):
    return await Market.objects.select_all().get(id=market_id)


class MarketCreateRequest(BaseModel):
    name: str
    address: Optional[str]
    city: str
    country: Optional[str] = "Bulgaria"
    description: str
    owner_id: int
    maintainer_ids: list[int]


@router.post("/markets/", status_code=201, response_model=MarketResponse)
async def create_market(market: MarketCreateRequest):
    maintainers = await Artisan.objects.filter(
        id__in=market.maintainer_ids,
    ).all()
    owner = await Artisan.objects.get(id=market.owner_id)

    return await Market.objects.create(
        **market.model_dump(exclude={"maintainer_ids", "owner_id"}),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        owner=owner,
        maintainers=maintainers,
    )


class MarketPatchRequest(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    maintainer_ids: Optional[list[int]] = None


class MarketPutRequest(BaseModel):
    name: str
    address: Optional[str]
    city: str
    country: Optional[str]
    description: str
    maintainer_ids: list[int]


@router.patch("/markets/{market_id}/", response_model=MarketResponse)
@db.base_ormar_config.database.transaction()
async def patch_market(
    market_id: int,
    market: MarketPatchRequest,
):
    market_exists = await Market.objects.filter(pk=market_id).exists()
    if not market_exists:
        raise ormar.NoMatch()

    update_data = market.model_dump(exclude_unset=True)
    return await Market.objects.update_or_create(
        id=market_id,
        updated_at=datetime.now(),
        **update_data,
    )


@router.put("/markets/{market_id}/", response_model=MarketResponse)
@db.base_ormar_config.database.transaction()
async def put_market(
    market_id: int,
    market: MarketPutRequest,
):
    market_exists = await Market.objects.filter(pk=market_id).exists()
    if not market_exists:
        raise ormar.NoMatch()

    return await Market.objects.update_or_create(
        id=market_id,
        updated_at=datetime.now(),
        **market.model_dump(),
    )


@router.delete("/markets/{market_id}/", status_code=204)
async def delete_market(market_id: int) -> None:
    await Market.objects.delete(id=market_id)
