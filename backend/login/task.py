from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.login.database import Task, get_db
from typing import List
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()  # Remove prefix here since we want /api/tasks

# Pydantic models for request/response
class TaskBase(BaseModel):
    title: str
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class TaskUpdate(BaseModel):
    completed: bool

# Get all tasks
@router.get("/api/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    try:
        logger.info("Fetching all tasks")
        tasks = db.query(Task).all()
        logger.info(f"Found {len(tasks)} tasks")
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Create a new task
@router.post("/api/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Creating new task: {task.title}")
        db_task = Task(
            title=task.title,
            completed=task.completed
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        logger.info(f"Task created successfully with ID: {db_task.id}")
        return db_task
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Update a task
@router.put("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    try:
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        db_task.completed = task.completed
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Delete a task
@router.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to delete task with ID: {task_id}")
        db_task = db.query(Task).filter(Task.id == task_id).first()
        
        if not db_task:
            logger.info(f"Task with ID {task_id} not found")
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Found task to delete: {db_task.title}")
        db.delete(db_task)
        db.commit()
        logger.info("Task deleted successfully")
        return {"message": "Task deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
