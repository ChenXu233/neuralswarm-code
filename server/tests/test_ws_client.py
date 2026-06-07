import pytest
from neuralswarm.api.ws_client import get_client_manager


def test_client_manager_singleton():
    cm = get_client_manager()
    assert cm is not None
    assert cm.list_clients() == []
