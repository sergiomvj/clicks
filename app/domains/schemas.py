from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DomainCreateRequest(BaseModel):
    domain: str = Field(min_length=3, max_length=255)
    warm_phase: int = Field(default=1, ge=1, le=4)
    daily_limit: int = Field(default=10, ge=1, le=100)

    @field_validator("domain")
    @classmethod
    def normalize_domain(cls, value: str) -> str:
        return value.strip().lower()


class DomainPhaseUpdateRequest(BaseModel):
    warm_phase: int = Field(ge=1, le=4)


class DomainHealthCheckResponse(BaseModel):
    id: UUID
    domain: str
    is_blacklisted: bool
    is_active: bool
    reputation_score: int
    bounce_rate: float
    health_status: str


class DomainResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    domain: str
    warm_phase: int
    daily_limit: int
    sends_today: int
    reputation_score: int
    bounce_rate: float
    is_blacklisted: bool
    is_active: bool
    health_status: str


class DomainListResponse(BaseModel):
    items: list[DomainResponse]
