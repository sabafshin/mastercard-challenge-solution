"""In-memory repository implementation with soft delete support"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, TypedDict, cast

from ..models.account import Account, AccountCreate, AccountResponse, AccountUpdate
from .base import AccountRepository

logger = logging.getLogger(__name__)


class AccountData(TypedDict):
    """Type definition for internal account data storage"""

    id: int
    name: str
    description: Optional[str]
    balance: float
    active: bool
    created_at: datetime
    updated_at: datetime


class InMemoryAccountRepository(AccountRepository):
    """In-memory implementation of AccountRepository with soft delete capability"""

    def __init__(self):
        self._accounts: Dict[int, AccountData] = {}
        self._next_id: int = 1

    def _get_next_id(self) -> int:
        """Generate next available ID"""
        current_id = self._next_id
        self._next_id += 1
        return current_id

    async def create(self, account: AccountCreate) -> AccountResponse:
        """Create a new account"""
        account_id = self._get_next_id()
        now = datetime.now(timezone.utc)

        account_data: AccountData = {
            "id": account_id,
            "name": account.name,
            "description": account.description,
            "balance": account.balance,
            "active": account.active,
            "created_at": now,
            "updated_at": now,
        }

        self._accounts[account_id] = account_data
        logger.info(f"Created account with ID: {account_id}")
        return AccountResponse(**account_data)

    async def get_by_id(self, account_id: int) -> Optional[AccountResponse]:
        """Get account by ID (only returns active accounts)"""
        if (account_data := self._accounts.get(account_id)) and account_data["active"]:
            return AccountResponse(**account_data)
        return None

    async def get_all(self, active_only: bool = False) -> List[AccountResponse]:
        """Get all accounts"""
        accounts = list(self._accounts.values())

        if active_only:
            accounts = [acc for acc in accounts if acc["active"]]

        return [AccountResponse(**acc) for acc in accounts]

    async def get_all_including_deleted(self) -> List[AccountResponse]:
        """Get all accounts including soft-deleted ones (for admin purposes)"""
        accounts = list(self._accounts.values())
        return [AccountResponse(**acc) for acc in accounts]

    async def update(
        self, account_id: int, account: Account
    ) -> Optional[AccountResponse]:
        """Update an existing account (full replacement) - only active accounts"""
        if not (existing := self._accounts.get(account_id)) or not existing["active"]:
            return None

        # Compact update using cast for type safety, exclude computed fields
        updated_data = cast(
            AccountData,
            existing
            | account.model_dump(exclude={"display_balance"})
            | {"id": account_id, "updated_at": datetime.now(timezone.utc)},
        )

        self._accounts[account_id] = updated_data
        logger.info(f"Updated account ID: {account_id}")
        return AccountResponse(**updated_data)

    async def partial_update(
        self, account_id: int, account: AccountUpdate
    ) -> Optional[AccountResponse]:
        """Partially update an existing account - only active accounts"""
        if not (existing := self._accounts.get(account_id)) or not existing["active"]:
            return None

        # Compact partial update using cast for type safety
        updated_data = cast(
            AccountData,
            existing
            | account.model_dump(exclude_unset=True, exclude={"display_balance"})
            | {"updated_at": datetime.now(timezone.utc)},
        )

        self._accounts[account_id] = updated_data
        logger.info(f"Partially updated account ID: {account_id}")
        return AccountResponse(**updated_data)

    async def delete(self, account_id: int) -> bool:
        """Delete an account (soft delete - marks as inactive)"""
        if existing := self._accounts.get(account_id):
            existing.update({"active": False, "updated_at": datetime.now(timezone.utc)})
            logger.info(f"Soft deleted account ID: {account_id} (marked as inactive)")
            return True
        return False

    async def exists(self, account_id: int) -> bool:
        """Check if account exists and is active"""
        return bool((account := self._accounts.get(account_id)) and account["active"])
