from fastapi import FastAPI
from backend.download_handler import LinkHandler
from backend.session_handler import create_session, get_session, delete_session

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

