import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.bruteforce import BruteforceRequest, BruteforceResponse, TaskStatus
from app.cruds import bruteforce as bruteforce_crud
from app.services.task_manager import task_manager
from app.core.config import settings

router = APIRouter()


@router.post("/start", response_model=BruteforceResponse)
async def start_bruteforce(
    request: BruteforceRequest,
    db: Session = Depends(get_db),
    user_id: str = "anonymous"  # В реальном приложении получаем из токена
):
    """Запуск новой задачи брутфорса"""
    
    # Используем переданный task_id или генерируем новый
    task_id = getattr(request, 'task_id', None) or str(uuid.uuid4())
    
    # Используем дефолтный charset если не указан
    charset = request.charset or settings.default_charset
    
    # Ограничиваем максимальную длину
    max_length = min(request.max_length, settings.max_password_length)
    
    # Запускаем асинхронную задачу
    await task_manager.start_bruteforce_task(
        task_id=task_id,
        hash_type=request.hash_type,
        target_hash=request.target_hash,
        charset=charset,
        max_length=max_length,
        user_id=user_id
    )
    
    return BruteforceResponse(
        task_id=task_id,
        message=f"Задача брутфорса запущена. Подключитесь к WebSocket /ws/{task_id} для получения уведомлений."
    )


@router.get("/tasks", response_model=List[TaskStatus])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: str = "anonymous"
):
    """Получение списка задач пользователя"""
    tasks = bruteforce_crud.get_tasks(db, user_id, skip, limit)
    return [
        TaskStatus(
            task_id=task.task_id,
            status=task.status,
            hash_type=task.hash_type,
            progress=task.progress,
            current_combination=task.current_combination,
            combinations_per_second=task.combinations_per_second,
            result=task.result,
            elapsed_time=task.elapsed_time,
            created_at=task.created_at,
            completed_at=task.completed_at
        )
        for task in tasks
    ]


@router.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """Получение статуса конкретной задачи"""
    task = bruteforce_crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return TaskStatus(
        task_id=task.task_id,
        status=task.status,
        hash_type=task.hash_type,
        progress=task.progress,
        current_combination=task.current_combination,
        combinations_per_second=task.combinations_per_second,
        result=task.result,
        elapsed_time=task.elapsed_time,
        created_at=task.created_at,
        completed_at=task.completed_at
    )


@router.delete("/task/{task_id}")
async def cancel_task(task_id: str, db: Session = Depends(get_db)):
    """Отмена активной задачи"""
    success = task_manager.cancel_task(task_id)
    if success:
        return {"message": f"Задача {task_id} отменена"}
    else:
        raise HTTPException(status_code=404, detail="Активная задача не найдена")


@router.get("/active-tasks")
async def get_active_tasks():
    """Получение списка активных задач"""
    active_tasks = task_manager.get_active_tasks()
    return {
        "active_tasks": list(active_tasks.keys()),
        "count": len(active_tasks)
    }


@router.get("/demo-hash/{password}")
async def create_demo_hash(password: str, hash_type: str = "md5"):
    """Создание демонстрационного хеша для тестирования"""
    import hashlib
    
    hash_functions = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512
    }
    
    if hash_type not in hash_functions:
        raise HTTPException(status_code=400, detail="Неподдерживаемый тип хеша")
    
    hash_func = hash_functions[hash_type]
    result_hash = hash_func(password.encode()).hexdigest()
    
    return {
        "password": password,
        "hash_type": hash_type,
        "hash": result_hash,
        "message": f"Используйте этот хеш для тестирования брутфорса: {result_hash}"
    } 