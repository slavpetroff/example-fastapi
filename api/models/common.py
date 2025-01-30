import datetime

import ormar


class DateFieldsMixins:
    created_at = ormar.DateTime(
        default=datetime.datetime.now,
    )
    updated_at = ormar.DateTime(
        default=datetime.datetime.now,
    )

    deleted_at = ormar.DateTime(nullable=True)
