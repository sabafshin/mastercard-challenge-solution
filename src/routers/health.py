"""Health check endpoints"""

import logging
import sys
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends

from ..dependencies.repository import get_repository
from ..models.health import HealthResponse
from ..repositories.base import AccountRepository

logger = logging.getLogger(__name__)
router = APIRouter()


def get_system_status() -> Literal["healthy", "unhealthy"]:
    """Check system health using modern pattern matching"""

    try:
        # Check Python version compatibility
        match sys.version_info:
            case (3, 12, *_):
                version_check = "python_ok"
            case (3, minor, *_) if minor >= 10:
                version_check = "python_compatible"
            case _:
                version_check = "python_outdated"

        # Check environment configuration using centralized settings
        from ..main import settings

        match settings.repository_type.lower():
            case "memory" | "database":
                env_check = "env_ok"
            case _:
                env_check = "env_invalid"

        # Aggregate health status
        match (version_check, env_check):
            case ("python_ok" | "python_compatible", "env_ok"):
                return "healthy"
            case _:
                return "unhealthy"

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return "unhealthy"


@router.get("/health", status_code=200, response_model=HealthResponse)
async def health_check(
    repository: AccountRepository = Depends(get_repository),
) -> HealthResponse:
    """
    Enhanced Kubernetes health check endpoint with dependency validation.

    Returns service health status, timestamp, and version information.
    Includes basic repository connectivity check.
    """
    status = get_system_status()

    # Test repository connectivity
    try:
        # Simple connectivity test - check if we can call the repository
        await repository.get_all(active_only=True)
        if status == "unhealthy":
            status = "unhealthy"  # Keep unhealthy if system checks failed
    except Exception as e:
        logger.warning(f"Repository connectivity issue during health check: {e}")
        status = "unhealthy"

    return HealthResponse(
        status=status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        service="accounts-api",
        version="1.0.0",
    )
