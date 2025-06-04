"""Health check models"""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Health check response model"""

    model_config = ConfigDict(extra="forbid")

    status: Annotated[
        Literal["healthy", "unhealthy"], Field(description="Service status")
    ]
    timestamp: Annotated[str, Field(description="ISO 8601 timestamp")]
    service: Annotated[str, Field(description="Service name")]
    version: Annotated[str, Field(description="Service version")]
