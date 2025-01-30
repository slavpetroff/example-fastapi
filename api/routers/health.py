from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class DefaultResponse(BaseModel):
    status: str
    message: str
    error: str | None


@router.get("/health", response_model=DefaultResponse)
async def health_check():
    return DefaultResponse(
        status="ok", message="Service is healthy", error=None
    )
