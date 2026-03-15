from fastapi import FastAPI, HTTPException
from backend.download_handler import LinkHandler
from backend.session_handler import create_session, get_session, delete_session
from fastapi.responses import StreamingResponse
import os


app = FastAPI()

@app.post("/start-sesson")
def new_session(url: str):
    session_id = create_session(url)
    return {"session_id": session_id}

@app.get("/info")
def get_info(session_id:str):
    try:
        handler = get_session(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return handler.get_display_info()

@app.get("/streams")
def get_streams(session_id: str):
    try:
        handler = get_session(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    video, audio = handler.get_streams()
    return {"video": video, "audio": audio}

@app.post("/download", response_class=StreamingResponse)
def download(session_id: str, video_stream_id: str):
    try:
        handler = get_session(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    output_path = f"./output/{session_id}"
    os.makedirs(output_path, exist_ok=True)

    def generator():
        for percentage_completion in handler.download_content(video_id=video_stream_id, output_path=output_path):
            yield f"data: {percentage_completion}\n\n"
        yield "data: done\n\n"

    return StreamingResponse(generator(), media_type="text/event-stream")