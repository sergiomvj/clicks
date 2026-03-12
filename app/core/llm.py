from app.core.config import get_settings
from app.core.redis import get_redis_client


class LlmService:
    async def get_health_payload(self) -> dict[str, object]:
        settings = get_settings()
        active_layer = "layer1"
        model = settings.ollama_model or settings.anthropic_model or settings.openai_model
        try:
            redis_client = get_redis_client()
            candidate = await redis_client.get("llm:active_layer")
            if candidate:
                active_layer = candidate
        except RuntimeError:
            active_layer = "unavailable"

        return {
            "status": "ok",
            "service": "fbr-click-api",
            "active_llm_layer": active_layer,
            "active_model": model,
        }


_LLM_SERVICE = LlmService()


def get_llm_service() -> LlmService:
    return _LLM_SERVICE
