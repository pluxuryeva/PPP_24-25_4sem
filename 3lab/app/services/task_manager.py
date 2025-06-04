import asyncio
import time
import uuid
from typing import Dict, Optional, Callable
from datetime import datetime
from app.services.bruteforce import BruteforceService
from app.db.database import SessionLocal
from app.cruds import bruteforce as bruteforce_crud
from app.schemas.bruteforce import WebSocketMessage


class TaskManager:
    """Менеджер асинхронных задач как альтернатива Celery"""
    
    def __init__(self):
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.websocket_callbacks: Dict[str, Callable] = {}
        self.pending_messages: Dict[str, list] = {}  # Сообщения для задач без callback
    
    def register_websocket_callback(self, task_id: str, callback: Callable):
        """Регистрирует callback для отправки WebSocket сообщений"""
        self.websocket_callbacks[task_id] = callback
        
        # Отправляем накопленные сообщения
        if task_id in self.pending_messages:
            asyncio.create_task(self._send_pending_messages(task_id))
    
    async def _send_pending_messages(self, task_id: str):
        """Отправляет накопленные сообщения"""
        if task_id in self.pending_messages:
            for message in self.pending_messages[task_id]:
                await self.send_websocket_message(task_id, message)
            del self.pending_messages[task_id]
    
    def unregister_websocket_callback(self, task_id: str):
        """Удаляет callback для WebSocket"""
        if task_id in self.websocket_callbacks:
            del self.websocket_callbacks[task_id]
    
    async def send_websocket_message(self, task_id: str, message: dict):
        """Отправляет сообщение через WebSocket если есть активный callback"""
        if task_id in self.websocket_callbacks:
            try:
                await self.websocket_callbacks[task_id](message)
            except Exception as e:
                print(f"Ошибка отправки WebSocket сообщения: {e}")
        else:
            # Сохраняем сообщение для отправки при подключении
            if task_id not in self.pending_messages:
                self.pending_messages[task_id] = []
            self.pending_messages[task_id].append(message)
            print(f"📧 Сообщение сохранено для task {task_id}: {message['status']}")
    
    async def start_bruteforce_task(self, task_id: str, hash_type: str, target_hash: str,
                                  charset: str, max_length: int, user_id: str = None) -> str:
        """Запускает задачу брутфорса"""
        
        # Создаем запись в базе данных
        db = SessionLocal()
        try:
            from app.schemas.bruteforce import BruteforceRequest
            request = BruteforceRequest(
                hash_type=hash_type,
                target_hash=target_hash,
                charset=charset,
                max_length=max_length
            )
            bruteforce_crud.create_task(db, task_id, request, user_id)
        finally:
            db.close()
        
        # Запускаем асинхронную задачу
        task = asyncio.create_task(
            self._bruteforce_worker(task_id, hash_type, target_hash, charset, max_length)
        )
        self.active_tasks[task_id] = task
        
        return task_id
    
    async def _bruteforce_worker(self, task_id: str, hash_type: str, target_hash: str,
                               charset: str, max_length: int):
        """Воркер для выполнения брутфорса"""
        start_time = time.time()
        db = SessionLocal()
        
        try:
            # Обновляем статус на STARTED
            bruteforce_crud.start_task(db, task_id)
            
            # Отправляем WebSocket уведомление о начале
            start_message = {
                "status": "STARTED",
                "task_id": task_id,
                "hash_type": hash_type,
                "charset_length": len(charset),
                "max_length": max_length
            }
            await self.send_websocket_message(task_id, start_message)
            
            # Создаем сервис брутфорса
            bruteforce_service = BruteforceService(hash_type)
            
            async def progress_callback(progress: int, current_combination: str, combinations_per_second: int):
                """Callback для отправки прогресса"""
                # Обновляем в базе данных
                bruteforce_crud.update_task_progress(
                    db, task_id, progress, current_combination, combinations_per_second
                )
                
                # Отправляем WebSocket уведомление о прогрессе
                progress_message = {
                    "status": "PROGRESS",
                    "task_id": task_id,
                    "progress": progress,
                    "current_combination": current_combination,
                    "combinations_per_second": combinations_per_second
                }
                await self.send_websocket_message(task_id, progress_message)
            
            # Выполняем брутфорс (адаптируем синхронный метод для async)
            result = await self._run_bruteforce_async(
                bruteforce_service, target_hash, charset, max_length, progress_callback
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
            completion_message = {
                "status": "COMPLETED",
                "task_id": task_id,
                "result": found_password,
                "elapsed_time": elapsed_time
            }
            await self.send_websocket_message(task_id, completion_message)
            
        except Exception as e:
            # В случае ошибки
            error_message = {
                "status": "FAILED",
                "task_id": task_id,
                "result": f"Ошибка: {str(e)}"
            }
            await self.send_websocket_message(task_id, error_message)
            print(f"Ошибка в задаче {task_id}: {e}")
        
        finally:
            db.close()
            # Удаляем задачу из активных
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    async def _run_bruteforce_async(self, bruteforce_service, target_hash: str, charset: str, 
                                  max_length: int, progress_callback):
        """Асинхронная обертка для брутфорса"""
        start_time = time.time()
        attempts = 0
        total_combinations = sum(len(charset) ** i for i in range(1, max_length + 1))
        
        for combination in bruteforce_service.generate_combinations(charset, max_length):
            attempts += 1
            
            # Вычисляем хеш текущей комбинации
            current_hash = bruteforce_service.hash_string(combination)
            
            # Отчет о прогрессе чаще для коротких паролей
            if attempts % 100 == 0:  # Уменьшил с 1000 до 100
                progress = int((attempts / total_combinations) * 100)
                elapsed = time.time() - start_time
                combinations_per_second = int(attempts / elapsed) if elapsed > 0 else 0
                
                await progress_callback(
                    progress=min(progress, 99),
                    current_combination=combination,
                    combinations_per_second=combinations_per_second
                )
            
            # Проверяем совпадение
            if current_hash.lower() == target_hash.lower():
                return combination
            
            # Защита от бесконечного выполнения (максимум 10 минут)
            if time.time() - start_time > 600:
                break
            
            # Небольшая задержка для имитации работы и возможности переключения задач
            if attempts % 10 == 0:  # Уменьшил частоту задержек
                await asyncio.sleep(0.001)
        
        return None
    
    def get_active_tasks(self) -> Dict[str, asyncio.Task]:
        """Возвращает активные задачи"""
        return self.active_tasks.copy()
    
    def cancel_task(self, task_id: str) -> bool:
        """Отменяет активную задачу"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            del self.active_tasks[task_id]
            return True
        return False


# Глобальный экземпляр менеджера задач
task_manager = TaskManager() 