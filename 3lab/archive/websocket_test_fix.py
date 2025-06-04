#!/usr/bin/env python3
"""
ИСПРАВЛЕННЫЙ тест WebSocket - сначала подключение, потом задача!
"""

import asyncio
import websockets
import json
import httpx
import uuid

async def fixed_websocket_test():
    """Исправленный тест WebSocket"""
    
    print("=== ИСПРАВЛЕННЫЙ WebSocket тест ===")
    
    # 1. Генерируем task_id заранее
    task_id = str(uuid.uuid4())
    print(f"1. Сгенерирован task_id: {task_id}")
    
    # 2. СНАЧАЛА подключаемся к WebSocket
    uri = f"ws://127.0.0.1:8000/ws/{task_id}"
    print(f"2. Подключение к WebSocket: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket подключен!")
            
            # 3. ТЕПЕРЬ запускаем задачу с нашим task_id
            async with httpx.AsyncClient() as client:
                print("3. Запуск задачи с предопределенным ID...")
                
                # Создаем демо хеш
                response = await client.get("http://localhost:8000/api/bruteforce/demo-hash/abc")
                data = response.json()
                target_hash = data['hash']
                print(f"   Хеш для 'abc': {target_hash}")
                
                # Запускаем задачу с нашим task_id (нужно добавить это в API)
                task_data = {
                    "hash_type": "md5",
                    "target_hash": target_hash,
                    "max_length": 3,
                    "task_id": task_id  # Передаем наш ID
                }
                
                response = await client.post("http://localhost:8000/api/bruteforce/start", json=task_data)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Задача запущена: {result.get('task_id', task_id)}")
                else:
                    print(f"❌ Ошибка запуска: {response.text}")
                    return
            
            # 4. Слушаем WebSocket сообщения
            print("4. Ожидание сообщений...")
            for i in range(30):  # 30 секунд максимум
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    print(f"📨 Получено: {message}")
                    
                    # Пробуем распарсить JSON
                    try:
                        data = json.loads(message)
                        status = data.get('status', 'N/A')
                        print(f"   📋 Статус: {status}")
                        
                        if status == 'COMPLETED':
                            print(f"   🎯 Результат: {data.get('result', 'N/A')}")
                            break
                        elif status == 'FAILED':
                            print(f"   ❌ Ошибка: {data.get('result', 'N/A')}")
                            break
                            
                    except json.JSONDecodeError:
                        # Это обычное текстовое сообщение от сервера
                        pass
                        
                except asyncio.TimeoutError:
                    print(f"⏳ Таймаут {i+1}/30")
                    continue
                    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print(f"Тип: {type(e)}")

if __name__ == "__main__":
    asyncio.run(fixed_websocket_test()) 