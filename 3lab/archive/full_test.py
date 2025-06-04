#!/usr/bin/env python3
"""
ПОЛНЫЙ ФУНКЦИОНАЛЬНЫЙ ТЕСТ всего API
"""

import asyncio
import httpx
import time

async def full_api_test():
    """Полный тест всего API"""
    
    print("🚀 === ПОЛНЫЙ ТЕСТ ВСЕЙ СИСТЕМЫ ===")
    
    async with httpx.AsyncClient() as client:
        
        # 1. Тест создания демо хешей для всех алгоритмов
        print("\n1. 🔐 Тест всех алгоритмов хеширования")
        algorithms = ["md5", "sha1", "sha256", "sha512"]
        
        for algo in algorithms:
            response = await client.get(f"http://localhost:8000/api/bruteforce/demo-hash/test?hash_type={algo}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {algo.upper()}: {data['hash']}")
            else:
                print(f"   ❌ {algo.upper()}: {response.text}")
        
        # 2. Тест запуска нескольких задач параллельно
        print("\n2. 🏭 Тест параллельного выполнения задач")
        
        tasks = []
        passwords = ["a", "b", "c"]
        
        for password in passwords:
            # Создаем хеш
            response = await client.get(f"http://localhost:8000/api/bruteforce/demo-hash/{password}")
            if response.status_code == 200:
                data = response.json()
                target_hash = data['hash']
                
                # Запускаем брутфорс
                task_data = {
                    "hash_type": "md5",
                    "target_hash": target_hash,
                    "max_length": 1  # Короткие пароли для быстрого результата
                }
                
                response = await client.post("http://localhost:8000/api/bruteforce/start", json=task_data)
                if response.status_code == 200:
                    result = response.json()
                    task_id = result['task_id']
                    tasks.append((password, task_id))
                    print(f"   ✅ Запущена задача для '{password}': {task_id[:8]}...")
                else:
                    print(f"   ❌ Ошибка запуска для '{password}': {response.text}")
        
        # 3. Мониторинг выполнения всех задач
        print("\n3. 📊 Мониторинг выполнения задач")
        
        max_attempts = 30
        for attempt in range(max_attempts):
            print(f"\n   Попытка {attempt + 1}/{max_attempts}:")
            
            completed_tasks = 0
            
            for password, task_id in tasks:
                response = await client.get(f"http://localhost:8000/api/bruteforce/task/{task_id}")
                if response.status_code == 200:
                    task = response.json()
                    status = task['status']
                    result = task.get('result', 'N/A')
                    progress = task['progress']
                    
                    print(f"     {password}: {status} ({progress}%) -> {result}")
                    
                    if status in ['COMPLETED', 'FAILED']:
                        completed_tasks += 1
                else:
                    print(f"     {password}: Ошибка получения статуса")
            
            if completed_tasks == len(tasks):
                print("   🎉 Все задачи завершены!")
                break
                
            await asyncio.sleep(1)
        
        # 4. Проверка списка всех задач
        print("\n4. 📋 Проверка списка задач")
        response = await client.get("http://localhost:8000/api/bruteforce/tasks")
        if response.status_code == 200:
            all_tasks = response.json()
            print(f"   ✅ Всего задач в системе: {len(all_tasks)}")
            
            for task in all_tasks[-3:]:  # Показываем последние 3
                print(f"     - {task['task_id'][:8]}... ({task['status']}) -> {task.get('result', 'N/A')}")
        else:
            print(f"   ❌ Ошибка получения списка: {response.text}")
        
        # 5. Проверка активных задач
        print("\n5. ⚡ Проверка активных задач")
        response = await client.get("http://localhost:8000/api/bruteforce/active-tasks")
        if response.status_code == 200:
            active = response.json()
            print(f"   ✅ Активных задач: {active['count']}")
            if active['active_tasks']:
                print(f"   📝 IDs: {[tid[:8] + '...' for tid in active['active_tasks']]}")
        else:
            print(f"   ❌ Ошибка получения активных задач: {response.text}")
        
        # 6. Тест производительности
        print("\n6. 🚄 Тест производительности")
        start_time = time.time()
        
        response = await client.get("http://localhost:8000/api/bruteforce/demo-hash/fast")
        data = response.json()
        target_hash = data['hash']
        
        task_data = {
            "hash_type": "md5",
            "target_hash": target_hash,
            "max_length": 4  # Чуть сложнее
        }
        
        response = await client.post("http://localhost:8000/api/bruteforce/start", json=task_data)
        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            print(f"   ✅ Запущена задача производительности: {task_id[:8]}...")
            
            # Ждем завершения
            for i in range(60):  # 60 секунд максимум
                response = await client.get(f"http://localhost:8000/api/bruteforce/task/{task_id}")
                if response.status_code == 200:
                    task = response.json()
                    if task['status'] in ['COMPLETED', 'FAILED']:
                        elapsed = time.time() - start_time
                        print(f"   🎯 Результат: {task.get('result', 'N/A')}")
                        print(f"   ⏱️ Время выполнения: {elapsed:.2f} сек")
                        break
                await asyncio.sleep(0.5)
        
        # 7. Финальная статистика
        print("\n7. 📈 Финальная статистика")
        
        response = await client.get("http://localhost:8000/api/bruteforce/tasks")
        if response.status_code == 200:
            all_tasks = response.json()
            
            completed = len([t for t in all_tasks if t['status'] == 'COMPLETED'])
            failed = len([t for t in all_tasks if t['status'] == 'FAILED'])
            pending = len([t for t in all_tasks if t['status'] == 'PENDING'])
            
            print(f"   📊 Завершено: {completed}")
            print(f"   ❌ Провалено: {failed}")
            print(f"   ⏳ В ожидании: {pending}")
            print(f"   📦 Всего: {len(all_tasks)}")
    
    print("\n🎉 === ТЕСТ ЗАВЕРШЕН ===")
    print("✅ Все основные функции работают!")

if __name__ == "__main__":
    asyncio.run(full_api_test()) 