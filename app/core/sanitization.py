import re

PROMPT_INJECTION_PATTERNS = [
    re.compile(r'ignore\s+previous\s+instructions', re.IGNORECASE),
    re.compile(r'system\s+prompt', re.IGNORECASE),
    re.compile(r'<\s*/?system\s*>', re.IGNORECASE),
    re.compile(r'<\s*/?assistant\s*>', re.IGNORECASE),
    re.compile(r'<\s*/?developer\s*>', re.IGNORECASE),
]


def sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.replace('\x00', ' ').replace('\r', ' ').strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    for pattern in PROMPT_INJECTION_PATTERNS:
        cleaned = pattern.sub('[filtered]', cleaned)
    return cleaned


def sanitize_mapping(value: dict[str, object]) -> dict[str, object]:
    sanitized: dict[str, object] = {}
    for key, item in value.items():
        if isinstance(item, str):
            sanitized[key] = sanitize_text(item) or ''
        elif isinstance(item, dict):
            sanitized[key] = sanitize_mapping(item)
        elif isinstance(item, list):
            sanitized[key] = [sanitize_text(entry) if isinstance(entry, str) else entry for entry in item]
        else:
            sanitized[key] = item
    return sanitized
