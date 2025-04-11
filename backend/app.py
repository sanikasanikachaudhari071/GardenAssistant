from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, Depends, Header
from pydantic import BaseModel, Field
from backend.conversation.chat import chat_with_assistant
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from backend.login.task import router as task_router
from backend.login.database import Base, engine, get_db
from sqlalchemy.orm import Session
from backend.login.database import Task
import logging
import os
import tempfile
from pathlib import Path
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include task router without prefix (since it's already in the router)
app.include_router(task_router)

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="User ID is required")
    query: str = Field(..., description="Query text is required")

class TaskUpdate(BaseModel):
    completed: bool

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    logger.info(f"Received request: {request.method} {request.url}")
    logger.info(f"Request body: {body.decode()}")
    response = await call_next(request)
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = error.get("loc", ["unknown"])[-1]
        msg = error.get("msg", "Unknown error")
        errors.append(f"{field}: {msg}")
    error_message = "Validation error: " + ", ".join(errors)
    logger.error(f"Validation error: {error_message}")
    return JSONResponse(
        status_code=422,
        content={"detail": error_message}
    )

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    try:
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        db_task.completed = task.completed
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        logger.info(f"Processing chat request - user_id: {request.user_id}, query: {request.query}")
        response = chat_with_assistant(
            user_id=request.user_id,
            user_query=request.query,
            image_path=None
        )
        return {"response": response}
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing chat request: {error_message}")
        if "Failed to generate response from Groq" in error_message:
            raise HTTPException(
                status_code=500,
                detail="The AI service is currently unavailable. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {error_message}"
            )

@app.post("/chat/with_image")
async def chat_with_image(
    user_id: str = Form(...),
    query: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        logger.info(f"Received image upload - filename: {image.filename}, content_type: {image.content_type}")
        
        # Validate image file
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create a temporary directory if it doesn't exist
        temp_dir = Path("temp_images")
        temp_dir.mkdir(exist_ok=True)
        
        # Save uploaded file with original extension
        file_extension = Path(image.filename).suffix or '.jpg'
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension,
            dir=str(temp_dir)
        )
        temp_file_path = temp_file.name
        
        try:
            # Write image data to temp file
            content = await image.read()
            with open(temp_file_path, "wb") as f:
                f.write(content)
            
            logger.info(f"Saved image to: {temp_file_path}")
            logger.info(f"Processing chat request with image - user_id: {user_id}, query: {query}")
            
            # Process with your existing function
            response = chat_with_assistant(
                user_id=user_id,
                user_query=query,
                image_path=temp_file_path
            )
            
            return {"response": response}
        finally:
            # Clean up
            try:
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up temporary file: {e}")
                
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing chat request with image: {error_message}")
        raise HTTPException(status_code=500, detail=str(e))
    
