from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AgentOut(BaseModel):
    id: UUID
    slug: str
    display_name: str
    status: str
    repository_url: str | None = None
    scope_actions: list[str] = Field(default_factory=list)
    approval_required_actions: list[str] = Field(default_factory=list)
    owners: list[str] = Field(default_factory=list)
    kill_switch_active: bool = False
    last_heartbeat_at: datetime | None = None
    heartbeat_status: str = 'unknown'


class AgentHeartbeatRequest(BaseModel):
    status: str = Field(default='online', min_length=1)


class AgentHeartbeatOut(BaseModel):
    agent_id: UUID
    workspace_id: UUID
    status: str
    last_heartbeat_at: datetime


class AgentMarkdownCacheOut(BaseModel):
    id: UUID
    workspace_id: UUID
    agent_id: UUID
    file_name: str
    git_sha: str
    content: str
    repository_path: str
    refreshed_at: datetime
    updated_at: datetime


class AgentMarkdownCacheListOut(BaseModel):
    files: list[AgentMarkdownCacheOut] = Field(default_factory=list)


class AgentListOut(BaseModel):
    agents: list[AgentOut] = Field(default_factory=list)


class AgentValidationRequest(BaseModel):
    repository_path: str = Field(min_length=1)


class AgentValidationOut(BaseModel):
    repository_path: str
    valid: bool
    missing_files: list[str] = Field(default_factory=list)


class AgentRegistrationRequest(BaseModel):
    slug: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    repository_path: str = Field(min_length=1)


class AgentRegistrationOut(BaseModel):
    agent: AgentOut
    validation: AgentValidationOut


class AgentTokenRequest(BaseModel):
    agent_id: UUID
    ttl_minutes: int = Field(default=1440, ge=1440, le=1440)


class AgentTokenOut(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    expires_at: datetime
    agent: AgentOut


class AgentExecutionRequest(BaseModel):
    action_type: str = Field(min_length=1)
    payload: dict[str, object] = Field(default_factory=dict)


class AgentExecutionOut(BaseModel):
    status: str
    agent_id: UUID
    workspace_id: UUID
    action_type: str
    approval_id: UUID | None = None
    task_id: UUID | None = None
    message_id: UUID | None = None
    audit_log_status: str
    message: str


class AgentControlOut(BaseModel):
    workspace_id: UUID
    kill_switch_active: bool = False
    reason: str | None = None
    updated_by_user_id: UUID | None = None
    updated_at: datetime | None = None


class AgentControlUpdateRequest(BaseModel):
    active: bool
    reason: str = Field(min_length=1)


class ApprovalOut(BaseModel):
    id: UUID
    workspace_id: UUID
    agent_id: UUID | None = None
    action_type: str
    status: str
    requested_by_user_id: UUID | None = None
    resolved_by_user_id: UUID | None = None
    decision_notes: str | None = None
    expires_at: datetime | None = None
    expired: bool = False
    payload: dict[str, object]
    requested_at: datetime
    resolved_at: datetime | None = None


class ApprovalListOut(BaseModel):
    approvals: list[ApprovalOut] = Field(default_factory=list)


class ApprovalCreateRequest(BaseModel):
    agent_id: UUID | None = None
    action_type: str = Field(min_length=1)
    payload: dict[str, object] = Field(default_factory=dict)
    expires_in_hours: int = Field(default=24, ge=1, le=168)


class ApprovalDecisionRequest(BaseModel):
    status: str = Field(pattern='^(approved|rejected)$')
    decision_notes: str = Field(min_length=1)


class AuditLogOut(BaseModel):
    id: UUID
    workspace_id: UUID
    agent_id: UUID | None = None
    action_type: str
    trigger_type: str
    payload: dict[str, object]
    result: dict[str, object]
    created_at: datetime


class AuditLogListOut(BaseModel):
    logs: list[AuditLogOut] = Field(default_factory=list)
