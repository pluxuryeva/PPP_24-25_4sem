import json
from typing import Dict, List, Callable
from fastapi import WebSocket, APIRouter
from fastapi.websockets import WebSocketDisconnect

websocket_router = APIRouter()


class WebSocketManager:
    def __init__(self):
        # Словарь для хранения активных соединений по task_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Словарь для хранения соединений по user_id
        self.user_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str = None, user_id: str = None):
        """Подключение нового WebSocket клиента"""
        try:
            await websocket.accept()
            print(f"🔌 WebSocket подключен для task_id: {task_id}")
            
            if task_id:
                if task_id not in self.active_connections:
                    self.active_connections[task_id] = []
                self.active_connections[task_id].append(websocket)
                
                # Импортируем task_manager здесь чтобы избежать циклических импортов
                from app.services.task_manager import task_manager
                
                # Создаем callback функцию для конкретного task_id
                def create_callback(t_id: str) -> Callable:
                    async def callback(message: dict):
                        await self._send_to_task_connections(t_id, message)
                    return callback
                
                # Регистрируем callback для отправки сообщений в TaskManager
                task_manager.register_websocket_callback(task_id, create_callback(task_id))
                print(f"✅ Callback зарегистрирован для task_id: {task_id}")
            
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = []
                self.user_connections[user_id].append(websocket)
                
        except Exception as e:
            print(f"❌ Ошибка подключения WebSocket: {e}")
            raise
    
    def disconnect(self, websocket: WebSocket, task_id: str = None, user_id: str = None):
        """Отключение WebSocket клиента"""
        try:
            print(f"🔌 WebSocket отключен для task_id: {task_id}")
            
            if task_id and task_id in self.active_connections:
                if websocket in self.active_connections[task_id]:
                    self.active_connections[task_id].remove(websocket)
                if not self.active_connections[task_id]:
                    del self.active_connections[task_id]
                    # Удаляем callback из TaskManager
                    from app.services.task_manager import task_manager
                    task_manager.unregister_websocket_callback(task_id)
                    print(f"🗑️ Callback удален для task_id: {task_id}")
            
            if user_id and user_id in self.user_connections:
                if websocket in self.user_connections[user_id]:
                    self.user_connections[user_id].remove(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
                    
        except Exception as e:
            print(f"❌ Ошибка отключения WebSocket: {e}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Отправка персонального сообщения одному клиенту"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"❌ Ошибка отправки личного сообщения: {e}")
    
    async def _send_to_task_connections(self, task_id: str, message: dict):
        """Отправка сообщения всем подключениям для конкретной задачи"""
        if task_id in self.active_connections:
            message_str = json.dumps(message, ensure_ascii=False)
            disconnected = []
            
            print(f"📤 Отправка сообщения {task_id}: {message['status']}")
            
            for websocket in self.active_connections[task_id]:
                try:
                    await websocket.send_text(message_str)
                except Exception as e:
                    print(f"❌ Ошибка отправки в WebSocket: {e}")
                    disconnected.append(websocket)
            
            # Удаляем отключенные соединения
            for ws in disconnected:
                if ws in self.active_connections[task_id]:
                    self.active_connections[task_id].remove(ws)
        else:
            print(f"⚠️ Нет активных соединений для task_id: {task_id}")
    
    async def send_message_to_user(self, user_id: str, message: dict):
        """Отправка сообщения всем соединениям пользователя"""
        if user_id in self.user_connections:
            message_str = json.dumps(message, ensure_ascii=False)
            disconnected = []
            
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_text(message_str)
                except Exception as e:
                    print(f"❌ Ошибка отправки пользователю: {e}")
                    disconnected.append(websocket)
            
            # Удаляем отключенные соединения
            for ws in disconnected:
                if ws in self.user_connections[user_id]:
                    self.user_connections[user_id].remove(ws)


# Глобальный экземпляр менеджера
websocket_manager = WebSocketManager()


@websocket_router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket эндпоинт для подключения к конкретной задаче"""
    try:
        await websocket_manager.connect(websocket, task_id=task_id)
        
        while True:
            # Ожидаем сообщения от клиента (keep-alive)
            data = await websocket.receive_text()
            print(f"📨 Получено от клиента {task_id}: {data}")
            # Можно обработать команды от клиента
            await websocket_manager.send_personal_message(f"Получено: {data}", websocket)
            
    except WebSocketDisconnect:
        print(f"🔌 WebSocket отключился: {task_id}")
        websocket_manager.disconnect(websocket, task_id=task_id)
    except Exception as e:
        print(f"❌ Ошибка WebSocket endpoint: {e}")
        websocket_manager.disconnect(websocket, task_id=task_id)


@websocket_router.websocket("/ws/user/{user_id}")
async def user_websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket эндпоинт для подключения пользователя ко всем его задачам"""
    try:
        await websocket_manager.connect(websocket, user_id=user_id)
        
        while True:
            data = await websocket.receive_text()
            await websocket_manager.send_personal_message(f"Пользователь {user_id}: {data}", websocket)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, user_id=user_id)
    except Exception as e:
        print(f"❌ Ошибка WebSocket user endpoint: {e}")
        websocket_manager.disconnect(websocket, user_id=user_id) 