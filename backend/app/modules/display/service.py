# Display module service placeholder
class DisplayService:
    async def start_stream(self, video_url: str) -> dict:
        return {"status": "placeholder", "stream_url": video_url}
