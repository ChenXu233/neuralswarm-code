import pytest

from neuralswarm.services.llm.gateway import LLMGateway


@pytest.fixture
def gateway():
    return LLMGateway(base_url="http://localhost:3000", timeout=30)


def test_gateway_init(gateway):
    assert gateway.base_url == "http://localhost:3000"
    assert gateway.timeout == 30


def test_get_adapter_openai(gateway):
    adapter = gateway._get_adapter("openai")
    assert adapter.provider == "openai"


def test_get_adapter_claude(gateway):
    adapter = gateway._get_adapter("claude")
    assert adapter.provider == "claude"


def test_get_adapter_unknown(gateway):
    with pytest.raises(ValueError, match="Unknown provider"):
        gateway._get_adapter("unknown")
