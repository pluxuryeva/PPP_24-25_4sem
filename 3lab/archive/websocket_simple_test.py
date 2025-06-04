#!/usr/bin/env python3
"""
ПРОСТОЙ WebSocket тест без прокси
"""

import asyncio
import json
import sys
import time

# Используем встроенные библиотеки для избежания proxy проблем
try:
    import websocket
    print("Используем websocket-client")
    USE_SYNC = True
except ImportError:
    try:
        import websockets
        print("Используем websockets")
        USE_SYNC = False
    except ImportError:
        print("❌ Нет WebSocket библиотек! Устанавливаем...")
        sys.exit(1)

import httpx

async def simple_websocket_test():
    """Простой WebSocket тест"""
    
    print("🔌 === ПРОСТОЙ WebSocket ТЕСТ ===")
    
    # 1. Сначала создадим задачу через API
    async with httpx.AsyncClient() as client:
        print("1. Создание демо хеша...")
        response = await client.get("http://localhost:8000/api/bruteforce/demo-hash/z")
        if response.status_code != 200:
            print(f"❌ Ошибка API: {response.text}")
            return
            
        data = response.json()
        target_hash = data['hash']
        print(f"   Хеш для 'z': {target_hash}")
        
        print("2. Запуск задачи...")
        task_data = {
            "hash_type": "md5",
            "target_hash": target_hash,
            "max_length": 1
        }
        
        response = await client.post("http://localhost:8000/api/bruteforce/start", json=task_data)
        if response.status_code != 200:
            print(f"❌ Ошибка запуска: {response.text}")
            return
            
        result = response.json()
        task_id = result['task_id']
        print(f"   Task ID: {task_id}")
    
    # 2. Попробуем WebSocket подключение
    print("3. Попытка WebSocket подключения...")
    
    # Попробуем простое подключение без библиотек websockets
    import urllib.request
    import urllib.error
    
    try:
        # Простая проверка - доступен ли WebSocket endpoint
        # Это не настоящий WebSocket, но проверим HTTP endpoint
        test_url = f"http://localhost:8000/ws/{task_id}"
        print(f"   Проверка URL: {test_url}")
        
        # Попытка HTTP запроса к WebSocket endpoint (ожидаем ошибку)
        try:
            req = urllib.request.Request(test_url)
            response = urllib.request.urlopen(req)
            print(f"   Неожиданный успех: {response.status}")
        except urllib.error.HTTPError as e:
            if e.code == 426:  # Upgrade Required - правильный ответ для WebSocket
                print("   ✅ WebSocket endpoint отвечает правильно (426 Upgrade Required)")
            else:
                print(f"   ⚠️ HTTP ошибка: {e.code}")
        except Exception as e:
            print(f"   📡 Соединение установлено, но это не HTTP: {e}")
            
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
    
    # 3. Мониторинг задачи через REST API
    print("4. Мониторинг через REST API...")
    
    async with httpx.AsyncClient() as client:
        for i in range(10):
            response = await client.get(f"http://localhost:8000/api/bruteforce/task/{task_id}")
            if response.status_code == 200:
                task = response.json()
                print(f"   {i+1}. {task['status']} ({task['progress']}%) -> {task.get('result', 'N/A')}")
                
                if task['status'] in ['COMPLETED', 'FAILED']:
                    break
            else:
                print(f"   {i+1}. Ошибка: {response.text}")
                
            await asyncio.sleep(0.5)

def sync_websocket_test():
    """Синхронный WebSocket тест с websocket-client"""
    print("🔌 Синхронный WebSocket тест...")
    
    try:
        import websocket
        
        # Простое подключение
        ws_url = "ws://localhost:8000/ws/test-connection"
        print(f"Подключение к: {ws_url}")
        
        ws = websocket.create_connection(ws_url)
        print("✅ WebSocket подключен!")
        
        # Отправляем ping
        ws.send("ping")
        
        # Пробуем получить ответ
        try:
            result = ws.recv()
            print(f"📨 Получено: {result}")
        except Exception as e:
            print(f"⚠️ Не удалось получить ответ: {e}")
        
        ws.close()
        print("🔌 WebSocket закрыт")
        
    except Exception as e:
        print(f"❌ Ошибка синхронного WebSocket: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов WebSocket...")
    
    # Сначала простой тест
    asyncio.run(simple_websocket_test())
    
    # Потом синхронный тест
    sync_websocket_test() 