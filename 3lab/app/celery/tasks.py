import time
from datetime import datetime
from celery import current_task
from app.celery.celery_app import celery_app
from app.services.bruteforce import BruteforceService
from app.db.database import SessionLocal
from app.cruds import bruteforce as bruteforce_crud
from app.websocket.manager import websocket_manager
from app.schemas.bruteforce import WebSocketMessage


@celery_app.task(bind=True)
def bruteforce_task(self, task_id: str, hash_type: str, target_hash: str, 
                   charset: str, max_length: int):
    """
    Celery задача для выполнения брутфорса с WebSocket уведомлениями
    """
    start_time = time.time()
    db = SessionLocal()
    
    try:
        # Обновляем статус задачи на STARTED
        bruteforce_crud.start_task(db, task_id)
        
        # Отправляем WebSocket уведомление о начале
        start_message = WebSocketMessage(
            status="STARTED",
            task_id=task_id,
            hash_type=hash_type,
            charset_length=len(charset),
            max_length=max_length
        )
        websocket_manager.send_message_to_task(task_id, start_message.dict())
        
        # Создаем сервис брутфорса
        bruteforce_service = BruteforceService(hash_type)
        
        def progress_callback(progress: int, current_combination: str, combinations_per_second: int):
            """Callback для отправки прогресса через WebSocket"""
            # Обновляем в базе данных
            bruteforce_crud.update_task_progress(
                db, task_id, progress, current_combination, combinations_per_second
            )
            
            # Отправляем WebSocket уведомление о прогрессе
            progress_message = WebSocketMessage(
                status="PROGRESS",
                task_id=task_id,
                progress=progress,
                current_combination=current_combination,
                combinations_per_second=combinations_per_second
            )
            websocket_manager.send_message_to_task(task_id, progress_message.dict())
        
        # Выполняем брутфорс
        result = bruteforce_service.bruteforce(
            target_hash, charset, max_length, progress_callback
        )
        
        # Вычисляем время выполнения
        elapsed_seconds = int(time.time() - start_time)
        hours = elapsed_seconds // 3600
        minutes = (elapsed_seconds % 3600) // 60
        seconds = elapsed_seconds % 60
        elapsed_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Обновляем задачу как завершенную
        found_password = result if result else "Пароль не найден"
        bruteforce_crud.complete_task(db, task_id, found_password, elapsed_time)
        
        # Отправляем WebSocket уведомление о завершении
        completion_message = WebSocketMessage(
            status="COMPLETED",
            task_id=task_id,
            result=found_password,
            elapsed_time=elapsed_time
        )
        websocket_manager.send_message_to_task(task_id, completion_message.dict())
        
        return {
            "task_id": task_id,
            "result": found_password,
            "elapsed_time": elapsed_time
        }
        
    except Exception as e:
        # В случае ошибки
        error_message = WebSocketMessage(
            status="FAILED",
            task_id=task_id,
            result=f"Ошибка: {str(e)}"
        )
        websocket_manager.send_message_to_task(task_id, error_message.dict())
        raise
    
    finally:
        db.close() 