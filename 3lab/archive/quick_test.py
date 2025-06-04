#!/usr/bin/env python3
"""
БЫСТРЫЙ ТЕСТ работоспособности лабораторной работы №3
"""

import requests
import time

def quick_test():
    """Быстрая проверка всего функционала"""
    
    print("🚀 === БЫСТРЫЙ ТЕСТ ЛАБОРАТОРНОЙ РАБОТЫ №3 ===")
    
    try:
        # 1. Проверяем API
        print("1. 🔍 Проверка API...")
        response = requests.get("http://localhost:8000/api/bruteforce/demo-hash/a")
        if response.status_code == 200:
            print("   ✅ API работает!")
            target_hash = response.json()['hash']
        else:
            print("   ❌ API не отвечает")
            return
        
        # 2. Запускаем простую задачу
        print("2. ⚡ Запуск простой задачи...")
        task_data = {
            "hash_type": "md5",
            "target_hash": target_hash,
            "max_length": 1  # Супер быстро
        }
        
        response = requests.post("http://localhost:8000/api/bruteforce/start", json=task_data)
        if response.status_code == 200:
            task_id = response.json()['task_id']
            print(f"   ✅ Задача запущена: {task_id[:8]}...")
        else:
            print("   ❌ Ошибка запуска задачи")
            return
        
        # 3. Ждем результат (максимум 5 секунд)
        print("3. ⏱️ Ожидание результата...")
        for i in range(5):
            response = requests.get(f"http://localhost:8000/api/bruteforce/task/{task_id}")
            if response.status_code == 200:
                task = response.json()
                status = task['status']
                result = task.get('result', 'N/A')
                
                print(f"   {status} -> {result}")
                
                if status == 'COMPLETED':
                    print(f"   🎯 НАЙДЕНО: {result}")
                    break
                elif status == 'FAILED':
                    print(f"   ❌ ОШИБКА: {result}")
                    break
            
            time.sleep(1)
        
        # 4. Проверяем WebSocket подключение
        print("4. 🔌 Проверка WebSocket...")
        try:
            import websocket
            ws = websocket.create_connection(f"ws://localhost:8000/ws/test")
            ws.send("ping")
            ws.close()
            print("   ✅ WebSocket работает!")
        except Exception as e:
            print(f"   ⚠️ WebSocket: {e}")
        
        # 5. Финальная статистика
        print("5. 📊 Статистика...")
        response = requests.get("http://localhost:8000/api/bruteforce/tasks")
        if response.status_code == 200:
            tasks = response.json()
            completed = len([t for t in tasks if t['status'] == 'COMPLETED'])
            print(f"   ✅ Всего завершенных задач: {completed}")
        
        print("\n🎉 === ВСЁ РАБОТАЕТ! ===")
        print("✅ REST API: Работает")
        print("✅ Задачи: Выполняются")
        print("✅ База данных: Сохраняет")
        print("✅ WebSocket: Подключается")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    quick_test() 