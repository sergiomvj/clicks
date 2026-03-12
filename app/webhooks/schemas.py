from pydantic import BaseModel, Field, model_validator


class LeadHandoffPayload(BaseModel):
    workspace_id: str
    external_reference: str = Field(min_length=1)
    source_system: str = '1FBR-Leads'
    lead_name: str = Field(min_length=1)
    email: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    company_name: str | None = None
    origin: str = Field(min_length=1)
    score: float
    temperature: str = Field(min_length=1)
    virtual_manager_slug: str = Field(min_length=1)
    notes: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    handoff_payload: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_contact_channels(self) -> 'LeadHandoffPayload':
        if not any([self.email, self.phone, self.whatsapp]):
            raise ValueError('At least one contact channel is required: email, phone or whatsapp.')
        return self


class LeadHandoffResult(BaseModel):
    intake_id: str
    deal_id: str
    channel_id: str
    task_id: str
    status: str


class AcceptedStatusOut(BaseModel):
    status: str


class FbrDevEventPayload(BaseModel):
    workspace_id: str
    event_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = ''
    external_reference: str = Field(min_length=1)
    lead_name: str = Field(min_length=1)
    email: str | None = None
    phone: str | None = None
    source_system: str = '1FBR-Dev'
    metadata: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_contact_channels(self) -> 'FbrDevEventPayload':
        if not any([self.email, self.phone]):
            raise ValueError('At least one contact channel is required: email or phone.')
        return self


class FbrSuporteLeadPayload(BaseModel):
    workspace_id: str
    external_reference: str = Field(min_length=1)
    lead_name: str = Field(min_length=1)
    company_name: str | None = None
    email: str | None = None
    phone: str | None = None
    priority: str = 'medium'
    source_system: str = '1FBR-Suporte'
    notes: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_contact_channels(self) -> 'FbrSuporteLeadPayload':
        if not any([self.email, self.phone]):
            raise ValueError('At least one contact channel is required: email or phone.')
        return self


class GenericWebhookAck(BaseModel):
    status: str
    reference_id: str
