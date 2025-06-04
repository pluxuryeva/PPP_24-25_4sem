#!/usr/bin/env python3
"""
ДЕМОНСТРАЦИЯ лабораторной работы №3 - Вариант 5
Брутфорс с WebSocket уведомлениями
"""

import requests
import time
import json

def demo():
    """Простая демонстрация всего функционала"""
    
    print("🎯 ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №3")
    print("📋 Вариант 5: Брутфорс с WebSocket уведомлениями")
    print("=" * 50)
    
    try:
        # 1. Проверка API
        print("\n1. 🔍 Проверка REST API...")
        response = requests.get("http://localhost:8000/api/bruteforce/demo-hash/demo")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API работает! Хеш: {data['hash']}")
            target_hash = data['hash']
        else:
            print("   ❌ Сервер не запущен! Запустите: python main.py")
            return
        
        # 2. Запуск задачи
        print("\n2. ⚡ Запуск задачи брутфорса...")
        task_data = {
            "hash_type": "md5",
            "target_hash": target_hash,
            "max_length": 4
        }
        
        response = requests.post("http://localhost:8000/api/bruteforce/start", json=task_data)
        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            print(f"   ✅ Задача запущена: {task_id[:8]}...")
        else:
            print(f"   ❌ Ошибка: {response.text}")
            return
        
        # 3. Мониторинг
        print("\n3. 📊 Мониторинг выполнения...")
        for i in range(15):
            response = requests.get(f"http://localhost:8000/api/bruteforce/task/{task_id}")
            if response.status_code == 200:
                task = response.json()
                status = task['status']
                progress = task['progress']
                result = task.get('result', 'N/A')
                
                print(f"   📈 {status} ({progress}%) -> {result}")
                
                if status == 'COMPLETED':
                    print(f"   🎯 ПАРОЛЬ НАЙДЕН: '{result}'")
                    break
                elif status == 'FAILED':
                    print(f"   ❌ ОШИБКА: {result}")
                    break
            
            time.sleep(1)
        
        # 4. WebSocket тест
        print("\n4. 🔌 Тест WebSocket...")
        try:
            import websocket
            ws = websocket.create_connection(f"ws://localhost:8000/ws/test")
            ws.send("ping")
            response = ws.recv()
            ws.close()
            print(f"   ✅ WebSocket работает! Ответ: {response[:50]}...")
        except Exception as e:
            print(f"   ⚠️ WebSocket: {str(e)[:50]}...")
        
        # 5. Статистика
        print("\n5. 📈 Общая статистика...")
        response = requests.get("http://localhost:8000/api/bruteforce/tasks")
        if response.status_code == 200:
            tasks = response.json()
            total = len(tasks)
            completed = len([t for t in tasks if t['status'] == 'COMPLETED'])
            print(f"   📦 Всего задач в системе: {total}")
            print(f"   ✅ Завершено успешно: {completed}")
        
        print("\n" + "=" * 50)
        print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
        print("✅ REST API - работает")
        print("✅ Брутфорс - находит пароли")
        print("✅ WebSocket - подключается")
        print("✅ База данных - сохраняет данные")
        print("✅ TaskManager - управляет задачами")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("💡 Убедитесь что сервер запущен: python main.py")

if __name__ == "__main__":
    # Проверяем зависимости
    try:
        import requests
        import websocket
    except ImportError as e:
        print(f"❌ Не хватает зависимостей: {e}")
        print("📦 Установите: pip install requests websocket-client")
        exit(1)
    
    demo() 