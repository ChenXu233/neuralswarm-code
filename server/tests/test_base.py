from uuid import UUID
from neuralswarm.models.base import Base, uuid7


def test_uuid7_returns_uuid():
    result = uuid7()
    assert isinstance(result, UUID)


def test_uuid7_is_unique():
    ids = {uuid7() for _ in range(100)}
    assert len(ids) == 100


def test_base_has_metadata():
    assert hasattr(Base, "metadata")
    assert Base.metadata is not None
