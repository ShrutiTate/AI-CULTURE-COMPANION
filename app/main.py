from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.crew_wrapper import CultureCrew

app = FastAPI(
    title="AI Culture Companion API",
    description="API for cultural insights and persona-based chat",
    version="1.0.0"
)
crew = CultureCrew()


class SummaryRequest(BaseModel):
    culture: str
    username: str


class ChatRequest(BaseModel):
    culture: str
    persona: str
    message: str
    username: str


@app.get("/")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Culture Companion API"}


@app.post("/summary")
def get_summary(req: SummaryRequest):
    """Generate a cultural summary with etiquette guidelines."""
    try:
        return crew.generate_summary(req.culture, req.username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat_persona(req: ChatRequest):
    """Chat with a cultural persona and get etiquette feedback."""
    try:
        return crew.chat_as_culture(req.culture, req.persona, req.message, req.username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes/{username}")
def get_user_notes(username: str):
    """Retrieve all saved notes for a user."""
    return {"notes": crew.get_notes(username)}
