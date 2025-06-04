"""FastAPI Accounts API - Main Application Module"""

import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI

from .routers import accounts, health


@dataclass(frozen=True)
class Settings:
    """Application settings with environment variable support and validation"""

    repository_type: str = os.getenv("REPOSITORY_TYPE", "memory")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    def __post_init__(self) -> None:
        """Validate settings"""
        # Validate repository type
        match self.repository_type.lower():
            case "memory" | "mem":
                object.__setattr__(self, "repository_type", "memory")
            case "database" | "db" | "postgres" | "postgresql":
                object.__setattr__(self, "repository_type", "database")
            case _:
                raise ValueError(f"Invalid repository type: {self.repository_type}")

        # Validate log level
        match self.log_level.upper():
            case "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL":
                object.__setattr__(self, "log_level", self.log_level.upper())
            case _:
                raise ValueError(f"Invalid log level: {self.log_level}")

        # Validate port range
        if not (1000 <= self.port <= 65535):
            raise ValueError(f"Port must be between 1000 and 65535, got {self.port}")


settings = Settings()

# Configure logging with modern format
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Accounts API...")
    logger.info(f"Repository type: {settings.repository_type}")
    logger.info(f"Log level: {settings.log_level}")

    yield

    # Shutdown
    logger.info("Shutting down Accounts API...")


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="Accounts API",
    version="1.0.0",
    description="A simple accounts management API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Include routers
app.include_router(health.router)
app.include_router(accounts.router)


# =============================================================================
# APPLICATION STARTUP
# =============================================================================


def main() -> None:
    """Main entry point for the application"""
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
