import json
import redis
from app.core.config import get_settings

class ConversationMemory:
    def __init__(self):
        self.client = redis.from_url(get_settings().redis_url, decode_responses=True)

    def get(self, conversation_id: str) -> list[dict]:
        raw = self.client.get(f"conversation:{conversation_id}")
        return json.loads(raw) if raw else []

    def append(self, conversation_id: str, role: str, content: str):
        history = self.get(conversation_id)
        history.append({"role": role, "content": content})
        history = history[-10:]
        self.client.setex(f"conversation:{conversation_id}", 3600, json.dumps(history))
