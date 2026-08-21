from pydantic import BaseModel


class StreamRequest(BaseModel):
    video_url: str
    target_width: int = 320
    target_height: int = 240
    fps: int = 15


class DisplayStatus(BaseModel):
    is_streaming: bool = False
    current_media: str = ""
