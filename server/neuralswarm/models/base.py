from uuid import UUID

from sqlalchemy.orm import DeclarativeBase
from uuid_extensions import uuid7


class Base(DeclarativeBase):
    pass


def uuid7_pk() -> UUID:
    """生成 UUID v7 主键"""
    return uuid7()
