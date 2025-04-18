# from backend.conversation.chat import chat_with_assistant
# from backend.memory.adddata import add_pdf_to_chroma

# if __name__ == "__main__":
#     # add_pdf_to_chroma(pdf_path=r"C:\Users\SANIKA CHAUDHARI\OneDrive\Desktop\Philodendron - Wikipedia.pdf")

#     user_id = input("Enter your user ID (or type 'exit' to quit): ")
#     while True:
#         # user_id = input("Enter your user ID (or type 'exit' to quit): ")
#         # if user_id.lower() == 'exit':
#         #     break  # Exit the loop if the user types 'exit'
        
#         user_query = input("Enter your query (or leave blank if not applicable): ")
        
#         # Ask if the user wants to add an image
#         add_image = input("Do you want to add an image? (yes/no): ").strip().lower()
#         image_url = ""
        
#         if add_image == 'yes':
#             image_url = input("Enter the image URL (e.g., http://127.0.0.1:5000/images/download.jpg): ")
        
#         # Call the chat_with_assistant function
#         assistant_response, messages = chat_with_assistant(user_id, user_query, image_url, [])
        
#         # Print the assistant's response
#         print("Assistant's response:", assistant_response)   

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from backend.conversation.chat import chat_with_assistant
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.login.task import router as task_router
from backend.login.database import Base, engine, get_db
import logging
import os
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include task router
app.include_router(task_router)

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="User ID is required")
    query: str = Field(..., description="Query text is required")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    logger.info(f"Received request: {request.method} {request.url}")
    
    # Only try to decode if it's not a multipart/form-data request
    if not request.headers.get("content-type", "").startswith("multipart/form-data"):
        try:
            logger.info(f"Request body: {body.decode()}")
        except UnicodeDecodeError:
            logger.info("Request body: [binary data]")
    else:
        logger.info("Request body: [multipart/form-data]")
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 