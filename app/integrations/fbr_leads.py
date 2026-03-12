from app.crm.schemas import DealStageEventOut
from app.integrations.fbr_ecosystem import send_stage_event_to_fbr_leads as send_stage_event


async def send_stage_event_to_fbr_leads(event: DealStageEventOut) -> dict[str, object]:
    return await send_stage_event(event.model_dump(mode='json'))
