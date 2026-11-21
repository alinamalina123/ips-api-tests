import uuid
import pytest

from src.api_client import PumpsApiClient


@pytest.fixture(scope="session")
def base_url() -> str:
    return "https://ips.alexgallax-edu.ru"


@pytest.fixture(scope="session")
def api_client(base_url: str) -> PumpsApiClient:
    return PumpsApiClient(base_url=base_url)


@pytest.fixture
def pump_id() -> str:
    """Уникальный идентификатор помпы для обеспечения независимости тестов."""
    return f"test-pump-{uuid.uuid4().hex[:8]}"