from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from login.task import router as task_router
import httpx
import os
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from login.database import Task, get_db
from pydantic import BaseModel

import json

load_dotenv()
app = FastAPI()
# the allowa api to acces the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include task router
app.include_router(task_router, prefix="/api")

class TaskUpdate(BaseModel):
    completed: bool

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




