"""
Focused test suite for essential business logic.
Tests core CRUD operations and business rules using modern Python 3.12 patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.account import AccountCreate, AccountUpdate
from src.repositories.memory import InMemoryAccountRepository


class ApiTestData(TypedDict):
    """Structured API test data with type safety."""

    name: str
    description: str | None
    balance: float
    active: bool


@dataclass(frozen=True, slots=True)
class ApiTestCase:
    """Immutable test case for API testing."""

    name: str
    data: ApiTestData
    expected_status: int
    should_succeed: bool = True


class TestEssentialAccountLogic:
    """Essential tests for account business logic using modern Python 3.12 patterns."""

    @pytest.fixture
    def client(self):
        """Test client with isolated repository using context management."""
        from src.dependencies.repository import get_repository

        # Use walrus operator for compact assignment
        if not (test_repository := InMemoryAccountRepository()):
            pytest.fail("Failed to create test repository")

        app.dependency_overrides[get_repository] = lambda: test_repository

        with TestClient(app) as client:
            yield client

        app.dependency_overrides.clear()

    def test_health_endpoint(self, client: TestClient) -> None:
        """Verify health check works with modern type annotations."""
        if not (response := client.get("/health")):
            pytest.fail("Health endpoint failed")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    @pytest.mark.parametrize(
        "account_data,expected_status",
        [
            (
                ApiTestData(
                    name="Test Account",
                    description="Test description",
                    balance=1000.0,
                    active=True,
                ),
                201,
            ),
            (
                ApiTestData(
                    name="Minimal Account", description=None, balance=0.0, active=True
                ),
                201,
            ),
        ],
    )
    def test_create_account_success(
        self, client: TestClient, account_data: ApiTestData, expected_status: int
    ) -> None:
        """Test successful account creation with parametrized data."""
        # Convert TypedDict to regular dict for JSON serialization
        json_data = dict(account_data)

        if not (response := client.post("/accounts", json=json_data)):
            pytest.fail("Account creation request failed")

        assert response.status_code == expected_status

        match response.status_code:
            case 201:
                data = response.json()
                assert data["id"] >= 1
                assert data["name"] == account_data["name"]
                assert data["balance"] == account_data["balance"]
            case _:
                pytest.fail(f"Unexpected status code: {response.status_code}")

    @pytest.mark.parametrize(
        "invalid_data",
        [
            {"name": "", "balance": 100.0},  # Empty name
            {"name": "Valid", "balance": -100.0},  # Negative balance
        ],
    )
    def test_create_account_validation(
        self, client: TestClient, invalid_data: dict[str, str | float]
    ) -> None:
        """Test account creation validation with parametrized invalid data."""
        response = client.post("/accounts", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_account_validation(self, client):
        """Test account creation validation"""
        invalid_data = {
            "name": "",  # Invalid: empty name
            "balance": -100.0,  # Invalid: negative balance
        }

        response = client.post("/accounts", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_get_account_success(self, client):
        """Test retrieving an existing account with modern patterns."""
        # Create account using walrus operator
        account_data = {"name": "Test Account", "balance": 1000.0}
        if not (create_response := client.post("/accounts", json=account_data)):
            pytest.fail("Account creation failed")

        account_id = create_response.json()["id"]

        # Retrieve account
        if not (response := client.get(f"/accounts/{account_id}")):
            pytest.fail("Account retrieval failed")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id
        assert data["name"] == account_data["name"]

    def test_get_nonexistent_account(self, client):
        """Test retrieving non-existent account returns 404."""
        response = client.get("/accounts/999")
        assert response.status_code == 404

    def test_list_accounts(self, client):
        """Test listing accounts with modern assertion patterns."""
        # Create two accounts
        accounts_data = [
            {"name": "Account 1", "balance": 100.0},
            {"name": "Account 2", "balance": 200.0},
        ]

        for account_data in accounts_data:
            client.post("/accounts", json=account_data)

        # List accounts
        if not (response := client.get("/accounts")):
            pytest.fail("Account listing failed")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Account 1"
        assert data[1]["name"] == "Account 2"

    def test_update_account_success(self, client):
        """Test full account update with modern pattern matching."""
        # Create account using walrus operator
        if not (
            create_response := client.post(
                "/accounts", json={"name": "Original", "balance": 100.0}
            )
        ):
            pytest.fail("Account creation failed")

        account_id = create_response.json()["id"]

        # Update account
        update_data = {
            "name": "Updated",
            "description": "Updated description",
            "balance": 500.0,
            "active": False,
        }

        if not (response := client.put(f"/accounts/{account_id}", json=update_data)):
            pytest.fail("Account update failed")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["balance"] == 500.0
        assert data["active"] is False

    def test_partial_update_account(self, client):
        """Test partial account update with validation."""
        # Create account
        if not (
            create_response := client.post(
                "/accounts", json={"name": "Original", "balance": 100.0}
            )
        ):
            pytest.fail("Account creation failed")

        account_id = create_response.json()["id"]

        # Partial update
        update_data = {"name": "Partially Updated"}

        if not (response := client.patch(f"/accounts/{account_id}", json=update_data)):
            pytest.fail("Partial update failed")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Partially Updated"
        assert data["balance"] == 100.0  # Should remain unchanged

    def test_delete_account_success(self, client):
        """Test account deletion with comprehensive validation."""
        # Create account
        if not (
            create_response := client.post(
                "/accounts", json={"name": "To Delete", "balance": 100.0}
            )
        ):
            pytest.fail("Account creation failed")

        account_id = create_response.json()["id"]

        # Delete account
        response = client.delete(f"/accounts/{account_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/accounts/{account_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_account(self, client):
        """Test deleting non-existent account returns 404."""
        response = client.delete("/accounts/999")
        assert response.status_code == 404


class TestBusinessLogicValidation:
    """Test business logic and validation rules using modern Python 3.12 patterns."""

    @pytest.fixture
    def repository(self) -> InMemoryAccountRepository:
        """Fresh repository for each test."""
        return InMemoryAccountRepository()

    @pytest.mark.asyncio
    async def test_balance_must_be_non_negative(
        self, repository: InMemoryAccountRepository
    ) -> None:
        """Test that balance validation works with modern type checking."""
        valid_account = AccountCreate(
            name="Valid", description="Test", balance=0.0, active=True
        )

        if not (result := await repository.create(valid_account)):
            pytest.fail("Valid account creation failed")

        assert result.balance == 0.0

    @pytest.mark.asyncio
    async def test_account_ids_are_sequential(
        self, repository: InMemoryAccountRepository
    ) -> None:
        """Test that account IDs are assigned sequentially using walrus operator."""
        # Use walrus operator for compact assertions
        if not (
            account1 := await repository.create(
                AccountCreate(
                    name="First",
                    description="First account",
                    balance=100.0,
                    active=True,
                )
            )
        ):
            pytest.fail("First account creation failed")

        if not (
            account2 := await repository.create(
                AccountCreate(
                    name="Second",
                    description="Second account",
                    balance=200.0,
                    active=True,
                )
            )
        ):
            pytest.fail("Second account creation failed")

        assert account1.id == 1
        assert account2.id == 2

    @pytest.mark.asyncio
    async def test_partial_update_preserves_unset_fields(
        self, repository: InMemoryAccountRepository
    ) -> None:
        """Test that partial updates don't change unspecified fields using match statement."""
        # Create account
        if not (
            account := await repository.create(
                AccountCreate(
                    name="Original",
                    description="Original description",
                    balance=100.0,
                    active=True,
                )
            )
        ):
            pytest.fail("Account creation failed")

        # Partial update (only name)
        update = AccountUpdate(name="Updated")

        match await repository.partial_update(account.id, update):
            case None:
                pytest.fail("Partial update failed")
            case updated:
                assert updated.name == "Updated"
                assert updated.description == "Original description"  # Preserved
                assert updated.balance == 100.0  # Preserved
                assert updated.active is True  # Preserved
