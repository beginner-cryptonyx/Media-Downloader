from fastapi import FastAPI
from backend.download_handler import LinkHandler

app = FastAPI()

@app.get('/info')
def get_info(url: str):
    handler = LinkHandler(url)
    return handler.get_display_info()


@app.get("/streams")
def get_streams(url: str):
    handler = LinkHandler(url)
    video, audio = handler.get_streams()
    return {"video": video, "audio": audio}