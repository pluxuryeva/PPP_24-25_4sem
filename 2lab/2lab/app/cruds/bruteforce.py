from sqlalchemy.orm import Session
import uuid
from typing import Optional

from app.models.models import BruteForceTask
from app.schemas.schemas import BruteForceTaskCreate


def create_bruteforce_task(db: Session, task: BruteForceTaskCreate, user_id: int) -> BruteForceTask:
    task_id = str(uuid.uuid4())
    
    db_task = BruteForceTask(
        task_id=task_id,
        hash=task.hash,
        charset=task.charset,
        max_length=min(task.max_length, 8),
        status="pending",
        progress=0.0,
        user_id=user_id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_by_id(db: Session, task_id: str) -> Optional[BruteForceTask]:
    return db.query(BruteForceTask).filter(BruteForceTask.task_id == task_id).first()


def update_task_status(db: Session, task_id: str, status: str, progress: float, result: Optional[str] = None) -> BruteForceTask:
    db_task = get_task_by_id(db, task_id)
    if db_task:
        db_task.status = status
        db_task.progress = progress
        if result:
            db_task.result = result
        db.commit()
        db.refresh(db_task)
    return db_task 