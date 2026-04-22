from app.core.config import get_settings
from app.core.redis import get_redis_client


class LlmService:
    def _build_layers(self) -> list[dict[str, object]]:
        settings = get_settings()
        return [
            {
                'layer': 'layer1',
                'provider': 'ollama',
                'label': 'Ollama',
                'model': settings.ollama_model or 'not-configured',
                'priority': 'primary',
                'configured': bool(settings.ollama_base_url and settings.ollama_model),
            },
            {
                'layer': 'layer2',
                'provider': 'anthropic',
                'label': 'Claude',
                'model': settings.anthropic_model or 'not-configured',
                'priority': 'secondary',
                'configured': bool(settings.anthropic_api_key and settings.anthropic_model),
            },
            {
                'layer': 'layer3',
                'provider': 'openai',
                'label': 'OpenAI',
                'model': settings.openai_model or 'not-configured',
                'priority': 'reserve',
                'configured': bool(settings.openai_api_key and settings.openai_model),
            },
        ]

    async def get_health_payload(self) -> dict[str, object]:
        layers = self._build_layers()
        active_layer = 'layer1'
        redis_state: dict[str, str] = {}

        try:
            redis_client = get_redis_client()
            candidate = await redis_client.get('llm:active_layer')
            if candidate:
                active_layer = candidate
            for layer in ('layer1', 'layer2', 'layer3'):
                status = await redis_client.get(f'llm:{layer}:status')
                if status:
                    redis_state[layer] = status
        except RuntimeError:
            active_layer = 'unavailable'

        for layer in layers:
            layer_name = str(layer['layer'])
            layer['status'] = redis_state.get(layer_name, 'unknown' if layer['configured'] else 'not-configured')
            layer['active'] = layer_name == active_layer

        active_model = next((str(layer['model']) for layer in layers if layer['active']), 'unavailable')

        return {
            'status': 'ok',
            'service': 'fbr-click-api',
            'active_llm_layer': active_layer,
            'active_model': active_model,
            'llm_layers': layers,
        }


_LLM_SERVICE = LlmService()


def get_llm_service() -> LlmService:
    return _LLM_SERVICE
