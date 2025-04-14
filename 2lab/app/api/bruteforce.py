from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User
from app.services.auth import get_current_user
from app.schemas.schemas import BruteForceTaskCreate, BruteForceTaskResponse, BruteForceTaskStatus
from app.cruds.bruteforce import create_bruteforce_task, get_task_by_id, update_task_status
from app.services.bruteforce import start_brute_force_task

router = APIRouter()


@router.post("/brut_hash", response_model=BruteForceTaskResponse)
def create_hash_brute_task(
    task: BruteForceTaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if task.max_length > 8:
        task.max_length = 8  # Ограничение в 8 символов
    
    db_task = create_bruteforce_task(db=db, task=task, user_id=current_user.id)
    
    # Запуск задачи брутфорса в отдельном потоке
    start_brute_force_task(
        task_id=db_task.task_id,
        hash_to_crack=db_task.hash,
        charset=db_task.charset,
        max_length=db_task.max_length,
        db_callback=lambda task_id, status, progress, result: update_task_status(db, task_id, status, progress, result)
    )
    
    return {"task_id": db_task.task_id}


@router.get("/get_status", response_model=BruteForceTaskStatus)
def get_task_status(task_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = get_task_by_id(db, task_id)
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    # Проверка, что задача принадлежит текущему пользователю
    if db_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")
    
    return {
        "status": db_task.status,
        "progress": db_task.progress,
        "result": db_task.result
    } 