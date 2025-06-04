#!/usr/bin/env python3
"""
Простой тестовый скрипт для проверки работы приложения
"""

import asyncio
import time
import httpx


async def test_bruteforce_api():
    """Тестирует API брутфорса"""
    base_url = "http://localhost:8000"
    
    print("=== Тестирование Bruteforce API ===")
    
    async with httpx.AsyncClient() as client:
        # 1. Создаем демо хеш
        print("\n1. Создание демо хеша...")
        response = await client.get(f"{base_url}/api/bruteforce/demo-hash/test")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Создан хеш для пароля 'test': {data['hash']}")
            target_hash = data['hash']
        else:
            print(f"✗ Ошибка создания хеша: {response.text}")
            return
        
        # 2. Запускаем задачу брутфорса
        print("\n2. Запуск задачи брутфорса...")
        task_data = {
            "hash_type": "md5",
            "target_hash": target_hash,
            "max_length": 4
        }
        
        response = await client.post(f"{base_url}/api/bruteforce/start", json=task_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Задача запущена: {result['task_id']}")
            task_id = result['task_id']
        else:
            print(f"✗ Ошибка запуска задачи: {response.text}")
            return
        
        # 3. Проверяем статус задачи несколько раз
        print("\n3. Мониторинг выполнения задачи...")
        for i in range(10):
            response = await client.get(f"{base_url}/api/bruteforce/task/{task_id}")
            if response.status_code == 200:
                task_status = response.json()
                print(f"Итерация {i+1}: Статус: {task_status['status']}, Прогресс: {task_status['progress']}%")
                
                if task_status['status'] in ['COMPLETED', 'FAILED']:
                    if task_status['result']:
                        print(f"✓ Результат: {task_status['result']}")
                    break
            
            await asyncio.sleep(2)
        
        # 4. Проверяем список всех задач
        print("\n4. Список всех задач...")
        response = await client.get(f"{base_url}/api/bruteforce/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print(f"✓ Найдено задач: {len(tasks)}")
            for task in tasks:
                print(f"  - {task['task_id']}: {task['status']}")
        
        # 5. Проверяем активные задачи
        print("\n5. Активные задачи...")
        response = await client.get(f"{base_url}/api/bruteforce/active-tasks")
        if response.status_code == 200:
            active = response.json()
            print(f"✓ Активных задач: {active['count']}")
            print(f"  IDs: {active['active_tasks']}")
    
    print("\n=== Тест завершен ===")


if __name__ == "__main__":
    print("Убедитесь, что сервер запущен: python main.py")
    print("Нажмите Enter для начала тестирования...")
    input()
    
    asyncio.run(test_bruteforce_api()) 