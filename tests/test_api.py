"""
Integration tests for the Accounts API endpoints.
Tests the complete HTTP API functionality using modern Python 3.12 patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

import pytest
from fastapi.testclient import TestClient


class ApiResponseData(TypedDict):
    """Structured API response data with type safety."""

    id: int
    name: str
    description: str | None
    balance: float
    active: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class EndpointTestCase:
    """Immutable test case for API endpoint testing."""

    name: str
    method: str
    endpoint: str
    data: dict | None = None
    expected_status: int = 200
    should_succeed: bool = True


class TestHealthEndpoint:
    """Test cases for health check endpoint using modern patterns."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check endpoint returns correct response with walrus operator."""
        if not (response := client.get("/health")):
            pytest.fail("Health check request failed")

        assert response.status_code == 200
        data = response.json()

        # Use match statement for validation
        match data:
            case {"status": "healthy", "service": "accounts-api", "version": "1.0.0"}:
                assert "timestamp" in data
            case _:
                pytest.fail(f"Unexpected health check response: {data}")


class TestAccountCRUDOperations:
    """Test cases for Account CRUD operations using modern Python 3.12 patterns."""

    def test_create_account_success(
        self, client: TestClient, sample_account_data
    ) -> None:
        """Test successful account creation with modern validation patterns."""
        if not (response := client.post("/accounts", json=sample_account_data)):
            pytest.fail("Account creation request failed")

        assert response.status_code == 201
        data = response.json()

        # Modern assertion patterns with walrus operator
        assert (account_id := data["id"]) == 1  # First account gets ID 1
        assert data["name"] == sample_account_data["name"]
        assert data["description"] == sample_account_data["description"]
        assert data["balance"] == sample_account_data["balance"]
        assert data["active"] == sample_account_data["active"]
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.parametrize("field_to_remove", ["name", "balance"])
    def test_create_account_validation_errors(
        self, client: TestClient, invalid_account_data, field_to_remove: str
    ) -> None:
        """Test account creation with invalid data using parametrization."""
        # Remove a required field to make it invalid
        test_data = dict(invalid_account_data)
        if field_to_remove in test_data:
            del test_data[field_to_remove]

        response = client.post("/accounts", json=test_data)

        assert response.status_code == 422  # Validation error
        error_data = response.json()
        assert "detail" in error_data

    def test_create_account_missing_required_fields(self, client: TestClient) -> None:
        """Test account creation with missing required fields."""
        incomplete_data = {"name": "Test Account"}  # Missing balance

        response = client.post("/accounts", json=incomplete_data)
        assert response.status_code == 422

    def test_get_account_success(self, client, sample_account_data):
        """Test retrieving an existing account"""
        # Create account first
        create_response = client.post("/accounts", json=sample_account_data)
        account_id = create_response.json()["id"]

        # Retrieve account
        response = client.get(f"/accounts/{account_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id
        assert data["name"] == sample_account_data["name"]

    def test_get_account_not_found(self, client):
        """Test retrieving a non-existing account"""
        response = client.get("/accounts/999")

        assert response.status_code == 404
        error_data = response.json()
        assert "Account with id 999 not found" in error_data["detail"]

    def test_list_accounts_empty(self, client):
        """Test listing accounts when none exist"""
        response = client.get("/accounts")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_accounts_with_data(self, client, sample_account_data):
        """Test listing accounts when some exist"""
        # Create multiple accounts
        client.post("/accounts", json=sample_account_data)
        client.post("/accounts", json={**sample_account_data, "name": "Second Account"})

        response = client.get("/accounts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[1]["id"] == 2

    def test_list_accounts_active_only(self, client):
        """Test listing only active accounts"""
        # Create active account
        active_account = {"name": "Active", "balance": 100.0, "active": True}
        client.post("/accounts", json=active_account)

        # Create inactive account
        inactive_account = {"name": "Inactive", "balance": 100.0, "active": False}
        client.post("/accounts", json=inactive_account)

        # Get all accounts
        response = client.get("/accounts")
        assert len(response.json()) == 2

        # Get only active accounts
        response = client.get("/accounts?active_only=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["active"] is True

    def test_update_account_success(self, client, sample_account_data):
        """Test successful full account update"""
        # Create account first
        create_response = client.post("/accounts", json=sample_account_data)
        account_id = create_response.json()["id"]

        # Update account
        update_data = {
            "name": "Updated Account",
            "description": "Updated description",
            "balance": 2000.0,
            "active": False,
        }

        response = client.put(f"/accounts/{account_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["balance"] == update_data["balance"]
        assert data["active"] == update_data["active"]

    def test_update_account_not_found(self, client):
        """Test updating a non-existing account"""
        update_data = {"name": "Test", "balance": 100.0}
        response = client.put("/accounts/999", json=update_data)

        assert response.status_code == 404

    def test_partial_update_account_success(
        self, client, sample_account_data, partial_update_data
    ):
        """Test successful partial account update"""
        # Create account first
        create_response = client.post("/accounts", json=sample_account_data)
        account_id = create_response.json()["id"]

        # Partial update
        response = client.patch(f"/accounts/{account_id}", json=partial_update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id
        assert data["name"] == partial_update_data["name"]
        assert data["balance"] == partial_update_data["balance"]
        # Unchanged fields should remain the same
        assert data["description"] == sample_account_data["description"]
        assert data["active"] == sample_account_data["active"]

    def test_partial_update_account_not_found(self, client, partial_update_data):
        """Test partial update of a non-existing account"""
        response = client.patch("/accounts/999", json=partial_update_data)

        assert response.status_code == 404

    def test_delete_account_success(self, client, sample_account_data):
        """Test successful account deletion"""
        # Create account first
        create_response = client.post("/accounts", json=sample_account_data)
        account_id = create_response.json()["id"]

        # Delete account
        response = client.delete(f"/accounts/{account_id}")

        assert response.status_code == 204  # No Content
        assert response.text == ""  # No response body

        # Verify account is deleted
        get_response = client.get(f"/accounts/{account_id}")
        assert get_response.status_code == 404

    def test_delete_account_not_found(self, client):
        """Test deleting a non-existing account"""
        response = client.delete("/accounts/999")

        assert response.status_code == 404


class TestAccountValidation:
    """Test cases for input validation"""

    def test_negative_balance_validation(self, client):
        """Test that negative balance is rejected"""
        invalid_data = {"name": "Test Account", "balance": -100.0}

        response = client.post("/accounts", json=invalid_data)
        assert response.status_code == 422

    def test_empty_name_validation(self, client):
        """Test that empty name is rejected"""
        invalid_data = {"name": "", "balance": 100.0}

        response = client.post("/accounts", json=invalid_data)
        assert response.status_code == 422

    def test_long_description_validation(self, client):
        """Test that overly long description is rejected"""
        invalid_data = {
            "name": "Test Account",
            "description": "A" * 600,  # Too long
            "balance": 100.0,
        }

        response = client.post("/accounts", json=invalid_data)
        assert response.status_code == 422

    def test_invalid_account_id_type(self, client):
        """Test that invalid account ID type is handled"""
        response = client.get("/accounts/invalid_id")
        assert response.status_code == 422


class TestBoundaryConditions:
    """Test cases for boundary conditions and edge cases"""

    def test_zero_balance_allowed(self, client):
        """Test that zero balance is allowed"""
        account_data = {"name": "Zero Balance Account", "balance": 0.0}

        response = client.post("/accounts", json=account_data)
        assert response.status_code == 201
        data = response.json()
        assert data["balance"] == 0.0

    def test_maximum_valid_name_length(self, client):
        """Test account creation with maximum valid name length"""
        account_data = {
            "name": "A" * 100,  # Maximum allowed length
            "balance": 100.0,
        }

        response = client.post("/accounts", json=account_data)
        assert response.status_code == 201

    def test_maximum_valid_description_length(self, client):
        """Test account creation with maximum valid description length"""
        account_data = {
            "name": "Test Account",
            "description": "A" * 500,  # Maximum allowed length
            "balance": 100.0,
        }

        response = client.post("/accounts", json=account_data)
        assert response.status_code == 201

    def test_partial_update_with_empty_data(self, client, sample_account_data):
        """Test partial update with no fields provided"""
        # Create account first
        create_response = client.post("/accounts", json=sample_account_data)
        account_id = create_response.json()["id"]

        # Partial update with empty data
        response = client.patch(f"/accounts/{account_id}", json={})

        assert response.status_code == 200
        # Account should remain unchanged
        data = response.json()
        assert data["name"] == sample_account_data["name"]
        assert data["balance"] == sample_account_data["balance"]

    def test_update_with_empty_data(self, client, sample_account_data):
        """Test full update with no fields provided"""
        # Create account first
        create_response = client.post("/accounts", json=sample_account_data)
        account_id = create_response.json()["id"]

        # Full update with empty data
        response = client.put(f"/accounts/{account_id}", json={})

        assert response.status_code == 422


class TestConcurrencyAndConsistency:
    """Test cases for data consistency"""

    def test_multiple_account_creation_unique_ids(self, client, sample_account_data):
        """Test that multiple accounts get unique, sequential IDs"""
        responses = []
        for i in range(5):
            account_data = {**sample_account_data, "name": f"Account {i}"}
            response = client.post("/accounts", json=account_data)
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 201

        # IDs should be sequential and unique
        ids = [response.json()["id"] for response in responses]
        assert ids == [1, 2, 3, 4, 5]

    def test_account_state_consistency_after_operations(
        self, client, sample_account_data
    ):
        """Test that account state remains consistent through multiple operations"""
        # Create account
        create_response = client.post("/accounts", json=sample_account_data)
        account_id = create_response.json()["id"]
        original_created_at = create_response.json()["created_at"]

        # Update account
        update_data = {"name": "Updated Name", "balance": 1500.0}
        patch_response = client.patch(f"/accounts/{account_id}", json=update_data)

        # Verify consistency
        data = patch_response.json()
        assert data["id"] == account_id
        assert data["created_at"] == original_created_at  # Should not change
        assert data["updated_at"] != original_created_at  # Should be updated
        assert data["name"] == update_data["name"]
        assert data["balance"] == update_data["balance"]
        # Unchanged fields should remain
        assert data["description"] == sample_account_data["description"]
        assert data["active"] == sample_account_data["active"]
