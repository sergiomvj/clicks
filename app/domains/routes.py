from typing import Annotated
from uuid import UUID

from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_workspace_id
from app.domains.schemas import (
    DomainCreateRequest,
    DomainHealthCheckResponse,
    DomainListResponse,
    DomainPhaseUpdateRequest,
    DomainResponse,
)
from app.domains.service import DomainService, get_domain_service

router = APIRouter(prefix="/domains", tags=["domains"])


@router.get("", response_model=DomainListResponse)
async def list_domains(
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    domain_service: Annotated[DomainService, Depends(get_domain_service)],
) -> DomainListResponse:
    items = await domain_service.list_domains(workspace_id)
    return DomainListResponse(items=items)


@router.post("", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def create_domain(
    payload: DomainCreateRequest,
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    domain_service: Annotated[DomainService, Depends(get_domain_service)],
) -> DomainResponse:
    try:
        return await domain_service.create_domain(workspace_id, payload)
    except UniqueViolationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Domain already exists for this workspace.",
        ) from exc


@router.patch("/{domain_id}/phase", response_model=DomainResponse)
async def update_domain_phase(
    domain_id: UUID,
    payload: DomainPhaseUpdateRequest,
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    domain_service: Annotated[DomainService, Depends(get_domain_service)],
) -> DomainResponse:
    try:
        return await domain_service.update_phase(workspace_id, domain_id, payload)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found.",
        ) from exc


@router.post("/{domain_id}/check-blacklist", response_model=DomainHealthCheckResponse)
async def check_domain_blacklist(
    domain_id: UUID,
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    domain_service: Annotated[DomainService, Depends(get_domain_service)],
) -> DomainHealthCheckResponse:
    try:
        return await domain_service.check_blacklist(workspace_id, domain_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found.",
        ) from exc
