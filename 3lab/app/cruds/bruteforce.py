from sqlalchemy.orm import Session
from app.models.bruteforce import BruteforceTask
from app.schemas.bruteforce import BruteforceRequest
from typing import List, Optional
from datetime import datetime


def create_task(db: Session, task_id: str, request: BruteforceRequest, user_id: str = None) -> BruteforceTask:
    db_task = BruteforceTask(
        task_id=task_id,
        hash_type=request.hash_type,
        target_hash=request.target_hash,
        charset=request.charset or "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        max_length=request.max_length,
        user_id=user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: str) -> Optional[BruteforceTask]:
    return db.query(BruteforceTask).filter(BruteforceTask.task_id == task_id).first()


def get_tasks(db: Session, user_id: str = None, skip: int = 0, limit: int = 100) -> List[BruteforceTask]:
    query = db.query(BruteforceTask)
    if user_id:
        query = query.filter(BruteforceTask.user_id == user_id)
    return query.offset(skip).limit(limit).all()


def update_task_progress(db: Session, task_id: str, progress: int, current_combination: str, 
                        combinations_per_second: int) -> Optional[BruteforceTask]:
    db_task = get_task(db, task_id)
    if db_task:
        db_task.progress = progress
        db_task.current_combination = current_combination
        db_task.combinations_per_second = combinations_per_second
        db_task.status = "PROGRESS"
        db.commit()
        db.refresh(db_task)
    return db_task


def complete_task(db: Session, task_id: str, result: str, elapsed_time: str) -> Optional[BruteforceTask]:
    db_task = get_task(db, task_id)
    if db_task:
        db_task.status = "COMPLETED"
        db_task.result = result
        db_task.elapsed_time = elapsed_time
        db_task.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
    return db_task


def start_task(db: Session, task_id: str) -> Optional[BruteforceTask]:
    db_task = get_task(db, task_id)
    if db_task:
        db_task.status = "STARTED"
        db.commit()
        db.refresh(db_task)
    return db_task 