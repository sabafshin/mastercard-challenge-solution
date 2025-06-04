"""Repository factory and dependency injection with modern Python 3.12 patterns"""

from __future__ import annotations

from functools import lru_cache

from ..repositories.base import AccountRepository
from ..repositories.memory import InMemoryAccountRepository


class RepositoryFactory:
    """Factory for creating repository instances with modern Python 3.12 patterns"""

    @staticmethod
    def create_account_repository(repository_type: str) -> AccountRepository:
        """Create account repository based on settings configuration using pattern matching"""
        match repository_type.lower():
            case "memory" | "mem":
                return InMemoryAccountRepository()
            case "database" | "db" | "postgres" | "postgresql":
                # Future implementation for production database
                raise NotImplementedError(
                    "Database repository not yet implemented. "
                    "For production deployment, implement PostgreSQL repository."
                )
            case "redis" | "cache":
                # Future implementation for Redis-backed repository
                raise NotImplementedError(
                    "Redis repository not yet implemented. "
                    "For caching layer, implement Redis repository."
                )
            case unknown_type:
                supported_types = ["memory", "database", "redis"]
                raise ValueError(
                    f"Unknown repository type: '{unknown_type}'. "
                    f"Supported types: {supported_types}"
                )


@lru_cache(maxsize=1)
def _create_repository_instance() -> AccountRepository:
    """Create cached repository instance using centralized settings"""
    # Import here to avoid circular imports
    from ..main import settings

    return RepositoryFactory.create_account_repository(settings.repository_type)


def get_repository() -> AccountRepository:
    """Get repository instance with caching and proper dependency injection

    Returns:
        AccountRepository: Configured repository instance

    Note:
        Uses lru_cache for singleton pattern instead of global variables.
        Repository type is determined by centralized Settings configuration.
    """
    return _create_repository_instance()


def clear_repository_cache() -> None:
    """Clear repository cache for testing purposes"""
    _create_repository_instance.cache_clear()
