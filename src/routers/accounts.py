"""Account management endpoints"""

import logging
from functools import wraps
from typing import Any, Callable, List, NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from ..dependencies.repository import get_repository
from ..models.account import Account, AccountCreate, AccountResponse, AccountUpdate
from ..repositories.base import AccountRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/accounts", tags=["accounts"])


def handle_exceptions(operation_name: str):
    """Decorator for consistent error handling across endpoints using modern pattern matching"""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                # Use match statement for sophisticated error handling
                match e:
                    case ValidationError() as ve:
                        logger.warning(f"Validation error in {operation_name}: {ve}")
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Validation error: {str(ve)}",
                        )
                    case ValueError() as ve:
                        logger.warning(f"Value error in {operation_name}: {ve}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid value: {str(ve)}",
                        )
                    case _:
                        logger.error(
                            f"Unexpected error in {operation_name}: {str(e)}",
                            exc_info=True,
                        )
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error while {operation_name}",
                        )

        return wrapper

    return decorator


def raise_not_found(account_id: int) -> NoReturn:
    """Helper function to raise 404 errors consistently"""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Account with id {account_id} not found",
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
@handle_exceptions("creating account")
async def create_account(
    account: AccountCreate, repository: AccountRepository = Depends(get_repository)
) -> AccountResponse:
    """
    Create a new account.

    The server assigns a unique ID to the new account.
    """
    return await repository.create(account)


@router.get("", response_model=List[AccountResponse])
@handle_exceptions("listing accounts")
async def list_accounts(
    active_only: bool = False, repository: AccountRepository = Depends(get_repository)
) -> List[AccountResponse]:
    """
    List all accounts.

    Optionally filter by active status using the 'active_only' query parameter.
    """
    return await repository.get_all(active_only=active_only)


@router.get("/{account_id}", response_model=AccountResponse)
@handle_exceptions("retrieving account")
async def get_account(
    account_id: int, repository: AccountRepository = Depends(get_repository)
) -> AccountResponse:
    """
    Get a specific account by ID.

    Returns 404 if account is not found.
    """
    if not (account := await repository.get_by_id(account_id)):
        raise_not_found(account_id)
    assert account is not None  # Help type checker
    return account


@router.put("/{account_id}", response_model=AccountResponse)
@handle_exceptions("updating account")
async def update_account(
    account_id: int,
    account: Account,
    repository: AccountRepository = Depends(get_repository),
) -> AccountResponse:
    """
    Update an existing account (full replacement).

    All fields must be provided. Returns 404 if account is not found.
    """
    if not (updated_account := await repository.update(account_id, account)):
        raise_not_found(account_id)
    assert updated_account is not None  # Help type checker
    return updated_account


@router.patch("/{account_id}", response_model=AccountResponse)
@handle_exceptions("partially updating account")
async def partial_update_account(
    account_id: int,
    account: AccountUpdate,
    repository: AccountRepository = Depends(get_repository),
) -> AccountResponse:
    """
    Partially update an existing account.

    Only provided fields will be updated. Returns 404 if account is not found.
    """
    if not (updated_account := await repository.partial_update(account_id, account)):
        raise_not_found(account_id)
    assert updated_account is not None  # Help type checker
    return updated_account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions("deleting account")
async def delete_account(
    account_id: int, repository: AccountRepository = Depends(get_repository)
) -> None:
    """
    Delete an account.

    Returns 204 No Content on successful deletion.
    Returns 404 if account is not found.
    """
    if not await repository.delete(account_id):
        raise_not_found(account_id)
    # 204 No Content response (no body)
