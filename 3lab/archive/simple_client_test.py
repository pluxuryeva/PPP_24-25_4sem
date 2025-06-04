#!/usr/bin/env python3
"""
Простой тест функционала через код клиента
"""

import asyncio
import httpx

async def test_simple():
    """Простой тест API"""
    
    print("=== Простой тест API ===")
    
    async with httpx.AsyncClient() as client:
        # 1. Тест demo-hash
        print("1. Тест создания демо хеша...")
        response = await client.get("http://localhost:8000/api/bruteforce/demo-hash/a")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Хеш для 'a': {data['hash']}")
            target_hash = data['hash']
        else:
            print(f"❌ Ошибка: {response.text}")
            return
        
        # 2. Тест запуска задачи
        print("2. Тест запуска задачи...")
        task_data = {
            "hash_type": "md5",
            "target_hash": target_hash,
            "max_length": 1  # Очень короткий пароль
        }
        
        response = await client.post("http://localhost:8000/api/bruteforce/start", json=task_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Задача запущена: {result['task_id']}")
            task_id = result['task_id']
        else:
            print(f"❌ Ошибка запуска: {response.text}")
            return
        
        # 3. Мониторинг задачи
        print("3. Мониторинг задачи...")
        for i in range(20):  # Увеличим количество проверок
            await asyncio.sleep(0.5)  # Проверяем чаще
            
            response = await client.get(f"http://localhost:8000/api/bruteforce/task/{task_id}")
            if response.status_code == 200:
                task = response.json()
                print(f"  Попытка {i+1}: {task['status']}, прогресс: {task['progress']}%, текущая: {task.get('current_combination', 'N/A')}")
                
                if task['status'] in ['COMPLETED', 'FAILED']:
                    print(f"✅ Результат: {task.get('result', 'N/A')}")
                    break
            else:
                print(f"❌ Ошибка получения статуса: {response.text}")
        
        # 4. Активные задачи
        print("4. Проверка активных задач...")
        response = await client.get("http://localhost:8000/api/bruteforce/active-tasks")
        if response.status_code == 200:
            active = response.json()
            print(f"✅ Активных задач: {active['count']}")
        
    print("=== Тест завершен ===")

if __name__ == "__main__":
    asyncio.run(test_simple()) 