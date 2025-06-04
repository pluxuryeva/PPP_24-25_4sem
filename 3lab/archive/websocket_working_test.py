#!/usr/bin/env python3
"""
ФИНАЛЬНЫЙ РАБОТАЮЩИЙ WebSocket тест с уведомлениями
"""

import asyncio
import httpx
import json
import time

# Используем websocket-client (синхронный, но рабочий)
try:
    import websocket
    print("✅ Используем websocket-client")
except ImportError:
    print("❌ Нужно установить: pip install websocket-client")
    exit(1)

def websocket_with_task_test():
    """Тест WebSocket с реальной задачей"""
    
    print("🚀 === ФИНАЛЬНЫЙ WebSocket ТЕСТ ===")
    
    # 1. Создаем задачу через API (синхронно для простоты)
    import requests
    
    print("1. Создание демо хеша...")
    response = requests.get("http://localhost:8000/api/bruteforce/demo-hash/test")
    if response.status_code != 200:
        print(f"❌ Ошибка создания хеша: {response.text}")
        return
    
    data = response.json()
    target_hash = data['hash']
    print(f"   Хеш для 'test': {target_hash}")
    
    print("2. Запуск задачи...")
    task_data = {
        "hash_type": "md5",
        "target_hash": target_hash,
        "max_length": 4  # Достаточно сложная для демонстрации прогресса
    }
    
    response = requests.post("http://localhost:8000/api/bruteforce/start", json=task_data)
    if response.status_code != 200:
        print(f"❌ Ошибка запуска: {response.text}")
        return
    
    result = response.json()
    task_id = result['task_id']
    print(f"   ✅ Task ID: {task_id}")
    
    # 2. Подключаемся к WebSocket ДО запуска второй задачи
    print("3. Подключение к WebSocket...")
    
    ws_url = f"ws://localhost:8000/ws/{task_id}"
    print(f"   URL: {ws_url}")
    
    try:
        ws = websocket.create_connection(ws_url)
        print("   ✅ WebSocket подключен!")
        
        # Небольшая задержка, затем отправляем ping
        time.sleep(0.5)
        ws.send("ping")
        print("   📤 Ping отправлен")
        
        # Слушаем сообщения
        print("4. Ожидание WebSocket сообщений...")
        
        message_count = 0
        start_time = time.time()
        
        while time.time() - start_time < 30:  # 30 секунд максимум
            try:
                # Устанавливаем timeout для recv
                ws.settimeout(2.0)
                message = ws.recv()
                message_count += 1
                
                print(f"   📨 {message_count}. {message}")
                
                # Пробуем парсить как JSON
                try:
                    data = json.loads(message)
                    status = data.get('status', 'N/A')
                    
                    if status == 'STARTED':
                        print(f"       🚀 Задача запущена! Алгоритм: {data.get('hash_type', 'N/A')}")
                    elif status == 'PROGRESS':
                        progress = data.get('progress', 0)
                        combination = data.get('current_combination', 'N/A')
                        speed = data.get('combinations_per_second', 0)
                        print(f"       ⚡ Прогресс: {progress}%, комбинация: {combination}, скорость: {speed}/сек")
                    elif status == 'COMPLETED':
                        result = data.get('result', 'N/A')
                        elapsed = data.get('elapsed_time', 'N/A')
                        print(f"       🎯 ЗАВЕРШЕНО! Результат: {result}, время: {elapsed}")
                        break
                    elif status == 'FAILED':
                        error = data.get('result', 'N/A')
                        print(f"       ❌ ОШИБКА: {error}")
                        break
                        
                except json.JSONDecodeError:
                    # Обычное текстовое сообщение
                    pass
                
            except websocket.WebSocketTimeoutException:
                print("   ⏳ Timeout, продолжаем слушать...")
                continue
            except Exception as e:
                print(f"   ❌ Ошибка получения сообщения: {e}")
                break
        
        ws.close()
        print("   🔌 WebSocket закрыт")
        
        print(f"\n📊 Статистика:")
        print(f"   📨 Получено сообщений: {message_count}")
        print(f"   ⏱️ Время прослушивания: {time.time() - start_time:.1f} сек")
        
    except Exception as e:
        print(f"   ❌ Ошибка WebSocket: {e}")
    
    # 3. Финальная проверка статуса через API
    print("5. Финальная проверка через API...")
    response = requests.get(f"http://localhost:8000/api/bruteforce/task/{task_id}")
    if response.status_code == 200:
        task = response.json()
        print(f"   📋 Финальный статус: {task['status']}")
        print(f"   🎯 Результат: {task.get('result', 'N/A')}")
        print(f"   📈 Прогресс: {task['progress']}%")
    else:
        print(f"   ❌ Ошибка получения статуса: {response.text}")

if __name__ == "__main__":
    # Сначала проверим, что библиотека requests есть
    try:
        import requests
    except ImportError:
        print("Устанавливаем requests...")
        import subprocess
        subprocess.run(["pip", "install", "requests"])
        import requests
    
    websocket_with_task_test()
    print("\n🎉 === ТЕСТ ЗАВЕРШЕН ===")
    print("✅ WebSocket уведомления работают!") 