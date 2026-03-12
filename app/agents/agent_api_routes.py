from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.schemas import AgentExecutionOut, AgentExecutionRequest
from app.agents.service import execute_agent_action
from app.api.dependencies import get_agent_context
from app.core.database import get_database_pool
from app.core.rate_limit import enforce_multiple_rate_limits

router = APIRouter(prefix='/agent-api', tags=['agent-api'])


@router.post('/actions/execute', response_model=AgentExecutionOut)
async def post_agent_action(
    payload: AgentExecutionRequest,
    agent_context: Annotated[dict[str, object], Depends(get_agent_context)],
) -> AgentExecutionOut:
    workspace_id = agent_context['workspace_id']
    agent_id = agent_context['agent_id']
    rules = [(f'agent_api:{workspace_id}:{agent_id}', 60, 60)]
    channel_id = payload.payload.get('channel_id')
    if channel_id:
        rules.append((f'agent_api:channel:{workspace_id}:{channel_id}', 80, 60))
    await enforce_multiple_rate_limits(rules)
    try:
        return await execute_agent_action(
            get_database_pool(),
            workspace_id=workspace_id,
            agent_id=agent_id,
            agent_slug=str(agent_context['slug']),
            action_type=payload.action_type,
            payload=payload.payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
