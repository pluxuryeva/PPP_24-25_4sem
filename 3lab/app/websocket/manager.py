import json
from typing import Dict, List
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
        await websocket.accept()
        
        if task_id:
            if task_id not in self.active_connections:
                self.active_connections[task_id] = []
            self.active_connections[task_id].append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, task_id: str = None, user_id: str = None):
        """Отключение WebSocket клиента"""
        if task_id and task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]
        
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Отправка персонального сообщения одному клиенту"""
        try:
            await websocket.send_text(message)
        except:
            pass
    
    def send_message_to_task(self, task_id: str, message: dict):
        """Отправка сообщения всем клиентам, подписанным на задачу"""
        if task_id in self.active_connections:
            message_str = json.dumps(message, ensure_ascii=False)
            for websocket in self.active_connections[task_id]:
                try:
                    # Используем asyncio для отправки в синхронном контексте
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        loop.create_task(websocket.send_text(message_str))
                    except RuntimeError:
                        # Если нет активного event loop, создаем новый
                        asyncio.run(websocket.send_text(message_str))
                except:
                    # Удаляем неактивные соединения
                    self.active_connections[task_id].remove(websocket)
    
    async def send_message_to_user(self, user_id: str, message: dict):
        """Отправка сообщения всем соединениям пользователя"""
        if user_id in self.user_connections:
            message_str = json.dumps(message, ensure_ascii=False)
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_text(message_str)
                except:
                    self.user_connections[user_id].remove(websocket)


# Глобальный экземпляр менеджера
websocket_manager = WebSocketManager()


@websocket_router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket эндпоинт для подключения к конкретной задаче"""
    await websocket_manager.connect(websocket, task_id=task_id)
    try:
        while True:
            # Ожидаем сообщения от клиента (keep-alive)
            data = await websocket.receive_text()
            # Можно обработать команды от клиента
            await websocket_manager.send_personal_message(f"Получено: {data}", websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, task_id=task_id)


@websocket_router.websocket("/ws/user/{user_id}")
async def user_websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket эндпоинт для подключения пользователя ко всем его задачам"""
    await websocket_manager.connect(websocket, user_id=user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.send_personal_message(f"Пользователь {user_id}: {data}", websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, user_id=user_id) 