"""
Unit tests for the Account Repository implementations.
Tests the database abstraction layer in isolation using modern Python 3.12 patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

import pytest

from src.models.account import Account, AccountCreate, AccountUpdate
from src.repositories.memory import InMemoryAccountRepository


class AccountTestData(TypedDict):
    """Structured account test data with type safety."""

    name: str
    description: str | None
    balance: float
    active: bool


@dataclass(frozen=True, slots=True)
class RepositoryTestCase:
    """Immutable test case for repository operations."""

    name: str
    data: AccountTestData
    expected_id: int | None = None
    should_succeed: bool = True


# Test data using modern Python 3.12 patterns
REPOSITORY_TEST_CASES: list[RepositoryTestCase] = [
    RepositoryTestCase(
        name="standard_account",
        data=AccountTestData(
            name="Standard Account",
            description="A standard test account",
            balance=1000.0,
            active=True,
        ),
        expected_id=1,
    ),
    RepositoryTestCase(
        name="minimal_account",
        data=AccountTestData(
            name="Minimal", description=None, balance=0.0, active=True
        ),
        expected_id=2,
    ),
    RepositoryTestCase(
        name="inactive_account",
        data=AccountTestData(
            name="Inactive Account",
            description="An inactive account",
            balance=500.0,
            active=False,
        ),
        expected_id=3,
    ),
]


class TestInMemoryAccountRepository:
    """Test cases for InMemoryAccountRepository using modern Python 3.12 patterns."""

    @pytest.fixture
    def repository(self) -> InMemoryAccountRepository:
        """Create a fresh repository for each test."""
        return InMemoryAccountRepository()

    @pytest.fixture
    def sample_account(self) -> AccountCreate:
        """Sample account for testing with modern type annotations."""
        return AccountCreate(
            name="Test Account",
            description="A test account",
            balance=1000.0,
            active=True,
        )

    @pytest.mark.asyncio
    async def test_create_account(
        self, repository: InMemoryAccountRepository, sample_account: AccountCreate
    ) -> None:
        """Test creating a new account with walrus operator for assertions."""
        if not (result := await repository.create(sample_account)):
            pytest.fail("Account creation failed")

        # Modern assertions with type safety
        assert result.id == 1  # First account gets ID 1
        assert result.name == sample_account.name
        assert result.description == sample_account.description
        assert result.balance == sample_account.balance
        assert result.active == sample_account.active
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_create_multiple_accounts_incremental_ids(
        self,
        repository: InMemoryAccountRepository,
    ) -> None:
        """Test that multiple accounts get incremental IDs using modern patterns."""
        created_accounts = []

        # Create multiple accounts and verify incremental IDs
        for i, test_case in enumerate(REPOSITORY_TEST_CASES[:3], 1):
            account_data = AccountCreate(**test_case.data)

            if not (created_account := await repository.create(account_data)):
                pytest.fail(f"Failed to create account: {test_case.name}")

            # Each account should get sequential IDs starting from 1
            assert created_account.id == i
            created_accounts.append(created_account)

        # Verify all accounts have unique sequential IDs
        account_ids = [acc.id for acc in created_accounts]
        assert account_ids == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_get_by_id_existing(
        self, repository: InMemoryAccountRepository, sample_account: AccountCreate
    ) -> None:
        """Test retrieving an existing account by ID using modern patterns."""
        if not (created_account := await repository.create(sample_account)):
            pytest.fail("Account creation failed")

        if not (retrieved_account := await repository.get_by_id(created_account.id)):
            pytest.fail("Account retrieval failed")

        assert retrieved_account.id == created_account.id
        assert retrieved_account.name == created_account.name

    @pytest.mark.asyncio
    async def test_get_by_id_non_existing(
        self, repository: InMemoryAccountRepository
    ) -> None:
        """Test retrieving a non-existing account."""
        result = await repository.get_by_id(999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_empty(self, repository: InMemoryAccountRepository) -> None:
        """Test getting all accounts when repository is empty."""
        accounts = await repository.get_all()
        assert accounts == []

    @pytest.mark.asyncio
    async def test_get_all_with_accounts(
        self, repository: InMemoryAccountRepository, sample_account: AccountCreate
    ) -> None:
        """Test getting all accounts using walrus operator."""
        if not (account1 := await repository.create(sample_account)):
            pytest.fail("First account creation failed")
        if not (account2 := await repository.create(sample_account)):
            pytest.fail("Second account creation failed")

        accounts = await repository.get_all()
        assert len(accounts) == 2
        assert any(acc.id == account1.id for acc in accounts)
        assert any(acc.id == account2.id for acc in accounts)

    @pytest.mark.asyncio
    async def test_get_all_active_only(
        self, repository: InMemoryAccountRepository
    ) -> None:
        """Test getting only active accounts with match statement for validation."""
        # Create active account
        active_account = AccountCreate(
            name="Active", description="Active account", balance=100.0, active=True
        )
        if not (created_active := await repository.create(active_account)):
            pytest.fail("Active account creation failed")

        # Create inactive account
        inactive_account = AccountCreate(
            name="Inactive", description="Inactive account", balance=100.0, active=False
        )
        await repository.create(inactive_account)

        # Get all accounts
        all_accounts = await repository.get_all(active_only=False)
        assert len(all_accounts) == 2

        # Get only active accounts
        active_accounts = await repository.get_all(active_only=True)
        assert len(active_accounts) == 1
        assert active_accounts[0].id == created_active.id

    @pytest.mark.asyncio
    async def test_update_existing_account(
        self, repository: InMemoryAccountRepository, sample_account: AccountCreate
    ) -> None:
        """Test updating an existing account using match statement for validation."""
        if not (created_account := await repository.create(sample_account)):
            pytest.fail("Account creation failed")

        update_data = Account(
            name="Updated Name",
            description="Updated description",
            balance=2000.0,
            active=False,
        )

        match await repository.update(created_account.id, update_data):
            case None:
                pytest.fail("Account update failed")
            case updated_account:
                assert updated_account.id == created_account.id
                assert updated_account.name == "Updated Name"
                assert updated_account.description == "Updated description"
                assert updated_account.balance == 2000.0
                assert updated_account.active is False
                assert updated_account.created_at == created_account.created_at
                assert updated_account.updated_at > created_account.updated_at

    @pytest.mark.asyncio
    async def test_update_non_existing_account(
        self, repository: InMemoryAccountRepository
    ) -> None:
        """Test updating a non-existing account."""
        update_data = Account(
            name="Test", description="Test description", balance=100.0, active=True
        )
        result = await repository.update(999, update_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_partial_update_existing_account(
        self, repository: InMemoryAccountRepository, sample_account: AccountCreate
    ) -> None:
        """Test partially updating an existing account with modern type checking."""
        if not (created_account := await repository.create(sample_account)):
            pytest.fail("Account creation failed")

        partial_update = AccountUpdate(name="Partially Updated", balance=1500.0)

        match await repository.partial_update(created_account.id, partial_update):
            case None:
                pytest.fail("Partial update failed")
            case updated_account:
                assert updated_account.id == created_account.id
                assert updated_account.name == "Partially Updated"
                assert (
                    updated_account.description == sample_account.description
                )  # Unchanged
                assert updated_account.balance == 1500.0
                assert updated_account.active == sample_account.active  # Unchanged

    @pytest.mark.asyncio
    async def test_partial_update_non_existing_account(
        self, repository: InMemoryAccountRepository
    ) -> None:
        """Test partially updating a non-existing account."""
        partial_update = AccountUpdate(name="Test")
        result = await repository.partial_update(999, partial_update)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_existing_account(
        self, repository: InMemoryAccountRepository, sample_account: AccountCreate
    ) -> None:
        """Test deleting an existing account with comprehensive validation."""
        if not (created_account := await repository.create(sample_account)):
            pytest.fail("Account creation failed")

        # Verify account exists
        assert await repository.exists(created_account.id) is True

        # Delete account
        result = await repository.delete(created_account.id)
        assert result is True

        # Verify account no longer exists
        assert await repository.exists(created_account.id) is False
        assert await repository.get_by_id(created_account.id) is None

    @pytest.mark.asyncio
    async def test_delete_non_existing_account(
        self, repository: InMemoryAccountRepository
    ) -> None:
        """Test deleting a non-existing account."""
        result = await repository.delete(999)
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_existing_account(
        self, repository: InMemoryAccountRepository, sample_account: AccountCreate
    ) -> None:
        """Test checking existence of an existing account."""
        if not (created_account := await repository.create(sample_account)):
            pytest.fail("Account creation failed")
        result = await repository.exists(created_account.id)
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_non_existing_account(
        self, repository: InMemoryAccountRepository
    ) -> None:
        """Test checking existence of a non-existing account."""
        result = await repository.exists(999)
        assert result is False
