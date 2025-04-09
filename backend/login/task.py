from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from login.database import Task, get_db
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

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
@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks

# Create a new task
@router.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(
        title=task.title,
        completed=task.completed
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Update a task
# In task.py, modify the update_task function
@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Only update completed status if provided in the request
    db_task.completed = task.completed
    
    db.commit()
    db.refresh(db_task)
    return db_task

# Delete a task
@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    try:
        print(f"Attempting to delete task with ID: {task_id}")
        db_task = db.query(Task).filter(Task.id == task_id).first()
        
        if not db_task:
            print(f"Task with ID {task_id} not found")
            raise HTTPException(status_code=404, detail="Task not found")
        
        print(f"Found task to delete: {db_task.title}")
        db.delete(db_task)
        db.commit()
        print("Task deleted successfully")
        return {"message": "Task deleted successfully"}
    except Exception as e:
        print(f"Error deleting task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
