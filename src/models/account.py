"""Account-related Pydantic models"""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class Account(BaseModel):
    """Base Account model for API operations"""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    name: Annotated[
        str, Field(min_length=1, max_length=100, description="Account name")
    ]
    description: Annotated[
        Optional[str],
        Field(default=None, max_length=500, description="Account description"),
    ]
    balance: Annotated[float, Field(ge=0, description="Account balance (non-negative)")]
    active: Annotated[bool, Field(default=True, description="Account active status")]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate account name using pattern matching for common issues"""
        cleaned = v.strip()

        # Use match statement for validation patterns
        match cleaned.lower():
            case "" | " " | "\t" | "\n":
                raise ValueError("Account name cannot be empty or whitespace only")
            case name if any(char in name for char in ["<", ">", "&", '"', "'"]):
                raise ValueError("Account name contains invalid characters")
            case name if name.startswith(("admin", "root", "system")):
                raise ValueError("Account name cannot start with reserved keywords")
            case _:
                return cleaned

    @computed_field
    @property
    def display_balance(self) -> str:
        """Format balance for display with proper currency formatting"""
        return f"${self.balance:,.2f}"


class AccountCreate(Account):
    """Model for creating new accounts"""

    pass


class AccountUpdate(BaseModel):
    """Model for partial account updates"""

    model_config = ConfigDict(extra="forbid")

    name: Annotated[Optional[str], Field(default=None, min_length=1, max_length=100)]
    description: Annotated[Optional[str], Field(default=None, max_length=500)]
    balance: Annotated[Optional[float], Field(default=None, ge=0)]
    active: Optional[bool] = None


class AccountResponse(Account):
    """Model for account API responses"""

    id: Annotated[int, Field(description="Unique account identifier")]
    created_at: Annotated[datetime, Field(description="Account creation timestamp")]
    updated_at: Annotated[datetime, Field(description="Account last update timestamp")]

    @computed_field
    @property
    def age_days(self) -> int:
        """Calculate account age in days"""
        return (datetime.now() - self.created_at.replace(tzinfo=None)).days

    @computed_field
    @property
    def status_description(self) -> str:
        """Provide human-readable status description"""
        match (self.active, self.balance):
            case (True, balance) if balance > 0:
                return "Active with balance"
            case (True, 0):
                return "Active, zero balance"
            case (False, _):
                return "Inactive account"
            case _:
                return "Unknown status"
