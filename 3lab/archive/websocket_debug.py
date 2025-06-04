#!/usr/bin/env python3
"""
Отладочный тест WebSocket соединения
"""

import asyncio
import websockets
import json
import httpx

async def debug_websocket():
    """Отладка WebSocket соединения"""
    
    print("=== Отладка WebSocket ===")
    
    # 1. Создаем задачу
    async with httpx.AsyncClient() as client:
        print("1. Создание задачи...")
        task_data = {
            "hash_type": "md5", 
            "target_hash": "0cc175b9c0f1b6a831c399e269772661",  # хеш для "a"
            "max_length": 2
        }
        
        response = await client.post("http://localhost:8000/api/bruteforce/start", json=task_data)
        result = response.json()
        task_id = result['task_id']
        print(f"Task ID: {task_id}")
    
    # 2. Пробуем подключиться к WebSocket без timeout параметра
    uri = f"ws://127.0.0.1:8000/ws/{task_id}"
    print(f"Подключение к: {uri}")
    
    try:
        # Убираем timeout из connect()
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket подключен!")
            
            # Отправляем ping
            await websocket.send("ping")
            print("📤 Ping отправлен")
            
            # Ждем ответов с таймаутом на уровне recv
            for i in range(10):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    print(f"📨 Получено: {message}")
                    
                    # Пробуем распарсить как JSON
                    try:
                        data = json.loads(message)
                        print(f"   📋 Статус: {data.get('status', 'N/A')}")
                        if data.get('status') in ['COMPLETED', 'FAILED']:
                            break
                    except json.JSONDecodeError:
                        pass  # Это не JSON сообщение
                        
                except asyncio.TimeoutError:
                    print(f"⏳ Тайм-аут {i+1}")
                    continue
                    
    except websockets.exceptions.InvalidHandshake as e:
        print(f"❌ Ошибка handshake: {e}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Соединение закрыто: {e}")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        print(f"Тип ошибки: {type(e)}")

if __name__ == "__main__":
    asyncio.run(debug_websocket()) 