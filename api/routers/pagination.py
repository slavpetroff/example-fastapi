from typing import TypeVar

from fastapi import Query
from fastapi_pagination import Page
from fastapi_pagination.customization import CustomizedPage, UseParamsFields


T = TypeVar("T")

DefaultPage = CustomizedPage[
    Page[T],
    UseParamsFields(
        # change default size to be 5, increase upper limit to 1 000
        size=Query(50, ge=1, le=1_000),
    ),
]
