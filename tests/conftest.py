"""
Shared test fixtures and configuration for the test suite.
Modern Python 3.12 patterns with advanced pytest features.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, TypedDict

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.memory import InMemoryAccountRepository


class TestAccountData(TypedDict):
    """Structured test account data with type safety."""

    name: str
    description: str | None
    balance: float
    active: bool


@dataclass(frozen=True, slots=True)
class TestScenario:
    """Immutable test scenario data for parametrized tests."""

    name: str
    description: str
    account_data: TestAccountData
    expected_status: int
    should_succeed: bool = True


# Modern pytest patterns with Python 3.12 features
TEST_SCENARIOS: list[TestScenario] = [
    TestScenario(
        name="valid_basic_account",
        description="Basic valid account creation",
        account_data=TestAccountData(
            name="Test Account",
            description="A test account",
            balance=1000.0,
            active=True,
        ),
        expected_status=201,
    ),
    TestScenario(
        name="valid_minimal_account",
        description="Minimal valid account with defaults",
        account_data=TestAccountData(
            name="Minimal Account", description=None, balance=0.0, active=True
        ),
        expected_status=201,
    ),
    TestScenario(
        name="invalid_empty_name",
        description="Invalid account with empty name",
        account_data=TestAccountData(
            name="", description="Valid description", balance=100.0, active=True
        ),
        expected_status=422,
        should_succeed=False,
    ),
    TestScenario(
        name="invalid_negative_balance",
        description="Invalid account with negative balance",
        account_data=TestAccountData(
            name="Valid Name",
            description="Valid description",
            balance=-100.0,
            active=True,
        ),
        expected_status=422,
        should_succeed=False,
    ),
]


@asynccontextmanager
async def isolated_repository() -> AsyncIterator[InMemoryAccountRepository]:
    """Async context manager for isolated repository testing."""
    repository = InMemoryAccountRepository()
    try:
        yield repository
    finally:
        # Clean up any resources if needed
        pass


@pytest.fixture
def client():
    """Create a test client with dependency injection using modern patterns."""
    from src.dependencies.repository import get_repository

    # Use walrus operator for compact assignment
    if not (test_repository := InMemoryAccountRepository()):
        pytest.fail("Failed to create test repository")

    app.dependency_overrides[get_repository] = lambda: test_repository

    with TestClient(app) as client:
        yield client

    # Modern cleanup pattern
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def repository():
    """Create a fresh repository for testing with async support."""
    async with isolated_repository() as repo:
        yield repo


@pytest.fixture(params=TEST_SCENARIOS, ids=lambda scenario: scenario.name)
def test_scenario(request) -> TestScenario:
    """Parametrized fixture providing test scenarios with modern type safety."""
    return request.param


@pytest.fixture
def sample_account_data() -> TestAccountData:
    """Modern typed sample account data for testing."""
    return TestAccountData(
        name="Test Account",
        description="A test account for unit testing",
        balance=1000.0,
        active=True,
    )


@pytest.fixture(
    params=[
        TestAccountData(name="", description="Valid", balance=100.0, active=True),
        TestAccountData(
            name="Valid", description="A" * 600, balance=100.0, active=True
        ),
        TestAccountData(name="Valid", description="Valid", balance=-100.0, active=True),
    ],
    ids=["empty_name", "long_description", "negative_balance"],
)
def invalid_account_data(request) -> TestAccountData:
    """Parametrized invalid account data for validation testing."""
    return request.param


@pytest.fixture
def partial_update_data() -> dict[str, str | float]:
    """Partial update data using modern type annotations."""
    return {"name": "Updated Account Name", "balance": 1500.0}


# Modern pytest markers for test categorization
pytest_marks = {
    "unit": pytest.mark.unit,
    "integration": pytest.mark.integration,
    "slow": pytest.mark.slow,
    "database": pytest.mark.database,
}
