from dataclasses import dataclass

from app.core.config import get_settings
from app.core.redis import get_redis_client


@dataclass(frozen=True)
class LlmLayer:
    layer: int
    model: str
    redis_key: str


class LlmService:
    async def get_health_payload(self) -> dict[str, object]:
        active_layer = await self.get_active_layer()
        return {
            "status": "ok",
            "llm_layer": active_layer.layer,
            "model": active_layer.model,
        }

    async def get_active_layer(self) -> LlmLayer:
        settings = get_settings()
        layers = (
            LlmLayer(1, settings.ollama_model, "llm:layer1:status"),
            LlmLayer(2, settings.anthropic_model, "llm:layer2:status"),
            LlmLayer(3, settings.openai_model, "llm:layer3:status"),
        )
        for layer in layers:
            if await self._is_layer_healthy(layer.redis_key):
                return layer
        return layers[2]

    async def _is_layer_healthy(self, redis_key: str) -> bool:
        redis_client = get_redis_client()
        status = await redis_client.get(redis_key)
        return status in {"ok", None}


def get_llm_service() -> LlmService:
    return LlmService()
