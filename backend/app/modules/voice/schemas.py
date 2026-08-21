from pydantic import BaseModel


class VoiceMessage(BaseModel):
    sender: str
    text: str
    timestamp: float


class VoiceIntent(BaseModel):
    intent: str
    confidence: float
    slots: dict = {}
