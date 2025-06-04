"""Abstract repository interfaces"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.account import Account, AccountCreate, AccountResponse, AccountUpdate


class AccountRepository(ABC):
    """Abstract repository interface for account persistence with enhanced type safety"""

    @abstractmethod
    async def create(self, account: AccountCreate) -> AccountResponse:
        """Create a new account"""
        pass

    @abstractmethod
    async def get_by_id(self, account_id: int) -> Optional[AccountResponse]:
        """Get account by ID"""
        pass

    @abstractmethod
    async def get_all(self, active_only: bool = False) -> List[AccountResponse]:
        """Get all accounts, optionally filtered by active status"""
        pass

    @abstractmethod
    async def update(
        self, account_id: int, account: Account
    ) -> Optional[AccountResponse]:
        """Update an existing account (full replacement)"""
        pass

    @abstractmethod
    async def partial_update(
        self, account_id: int, account: AccountUpdate
    ) -> Optional[AccountResponse]:
        """Partially update an existing account"""
        pass

    @abstractmethod
    async def delete(self, account_id: int) -> bool:
        """Delete an account"""
        pass

    @abstractmethod
    async def exists(self, account_id: int) -> bool:
        """Check if account exists"""
        pass
