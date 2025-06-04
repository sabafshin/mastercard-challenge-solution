"""Test the modern repository factory implementation"""

from unittest.mock import patch

import pytest

from src.dependencies.repository import (
    RepositoryFactory,
    clear_repository_cache,
    get_repository,
)
from src.repositories.memory import InMemoryAccountRepository


class TestRepositoryFactory:
    """Test repository factory with modern Python 3.12 patterns"""

    def test_create_memory_repository(self):
        """Test creating memory repository with various alias patterns"""
        # Test primary name
        repo = RepositoryFactory.create_account_repository("memory")
        assert isinstance(repo, InMemoryAccountRepository)

        # Test alias
        repo = RepositoryFactory.create_account_repository("mem")
        assert isinstance(repo, InMemoryAccountRepository)

        # Test case insensitive
        repo = RepositoryFactory.create_account_repository("MEMORY")
        assert isinstance(repo, InMemoryAccountRepository)

    def test_unsupported_repository_types(self):
        """Test that unsupported repository types raise proper errors"""
        with pytest.raises(
            NotImplementedError, match="Database repository not yet implemented"
        ):
            RepositoryFactory.create_account_repository("database")

        with pytest.raises(
            NotImplementedError, match="Database repository not yet implemented"
        ):
            RepositoryFactory.create_account_repository("postgres")

        with pytest.raises(
            NotImplementedError, match="Redis repository not yet implemented"
        ):
            RepositoryFactory.create_account_repository("redis")

        with pytest.raises(ValueError, match="Unknown repository type: 'invalid'"):
            RepositoryFactory.create_account_repository("invalid")

    def test_repository_caching(self):
        """Test that repository instances are properly cached"""
        # Clear cache first
        clear_repository_cache()

        # Get two instances
        repo1 = get_repository()
        repo2 = get_repository()

        # Should be the same instance due to caching
        assert repo1 is repo2

    @patch("src.main.settings")
    def test_get_repository_uses_settings(self, mock_settings):
        """Test that get_repository uses centralized settings"""
        # Clear cache to force recreation
        clear_repository_cache()

        # Mock settings
        mock_settings.repository_type = "memory"

        # Get repository
        repo = get_repository()
        assert isinstance(repo, InMemoryAccountRepository)

        # Clear cache for next test
        clear_repository_cache()

    def test_clear_cache_functionality(self):
        """Test that cache clearing works correctly"""
        # Get initial repository
        repo1 = get_repository()

        # Clear cache
        clear_repository_cache()

        # Get new repository - should be different instance
        repo2 = get_repository()

        # Both should be InMemoryAccountRepository but different instances
        assert isinstance(repo1, InMemoryAccountRepository)
        assert isinstance(repo2, InMemoryAccountRepository)
        assert repo1 is not repo2
