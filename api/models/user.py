import re

import ormar

from api import db
from api.models.common import DateFieldsMixins


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password: str) -> bool:
    return len(password) >= 8


class User(ormar.Model, DateFieldsMixins):
    ormar_config = db.base_ormar_config.copy(
        tablename="users",
        constraints=[ormar.IndexColumns("email", unique=True)],
    )

    id = ormar.Integer(primary_key=True)
    email = ormar.String(
        max_length=100,
        unique=True,
        nullable=False,
        validator=validate_email,
    )
    password = ormar.String(
        max_length=128,  # Increased for hashed passwords
        nullable=False,
        min_length=8,
        validator=validate_password,
    )
