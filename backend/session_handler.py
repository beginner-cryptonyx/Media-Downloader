import uuid
from backend.download_handler import LinkHandler

sessions = {}

def create_session(url:str):
    session_id = str(uuid.uuid4())
    sessions[session_id] = LinkHandler(url)
    return session_id

def get_session(session_id:str):
    handler = sessions.get(session_id) or None
    if handler is None:
        raise KeyError(f"The session id {session_id} is not found")
    return handler

def delete_session(session_id):
    sessions.pop(session_id, None)