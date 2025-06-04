#!/usr/bin/env python3
"""
БЫСТРЫЙ АВТОМАТИЧЕСКИЙ ТЕСТ всех компонентов лабораторной работы №3
"""

import requests
import subprocess
import time
import json

def test_api():
    """Тест REST API"""
    print("🔍 Тестирование REST API...")
    
    try:
        # 1. Демо хеш
        response = requests.get("http://localhost:8000/api/bruteforce/demo-hash/test", timeout=5)
        assert response.status_code == 200
        data = response.json()
        target_hash = data['hash']
        print(f"   ✅ Demo hash: {target_hash}")
        
        # 2. Запуск задачи
        task_data = {
            "hash_type": "md5",
            "target_hash": target_hash,
            "max_length": 4
        }
        response = requests.post("http://localhost:8000/api/bruteforce/start", json=task_data, timeout=5)
        assert response.status_code == 200
        task_id = response.json()['task_id']
        print(f"   ✅ Task started: {task_id[:8]}...")
        
        # 3. Проверка статуса
        response = requests.get(f"http://localhost:8000/api/bruteforce/task/{task_id}", timeout=5)
        assert response.status_code == 200
        print(f"   ✅ Task status: {response.json()['status']}")
        
        # 4. Список задач
        response = requests.get("http://localhost:8000/api/bruteforce/tasks", timeout=5)
        assert response.status_code == 200
        tasks_count = len(response.json())
        print(f"   ✅ Total tasks: {tasks_count}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API Error: {e}")
        return False

def test_websocket():
    """Тест WebSocket подключения"""
    print("🔌 Тестирование WebSocket...")
    
    try:
        import websocket
        
        # Попытка подключения
        ws = websocket.create_connection("ws://localhost:8000/ws/test-connection", timeout=5)
        ws.send("ping")
        response = ws.recv()
        ws.close()
        
        print(f"   ✅ WebSocket response: {response[:30]}...")
        return True
        
    except Exception as e:
        print(f"   ❌ WebSocket Error: {str(e)[:50]}...")
        return False

def test_algorithms():
    """Тест всех алгоритмов хеширования"""
    print("🔐 Тестирование алгоритмов...")
    
    algorithms = ["md5", "sha1", "sha256", "sha512"]
    success = 0
    
    for algo in algorithms:
        try:
            response = requests.get(f"http://localhost:8000/api/bruteforce/demo-hash/demo?hash_type={algo}", timeout=5)
            if response.status_code == 200:
                hash_value = response.json()['hash']
                print(f"   ✅ {algo.upper()}: {hash_value[:16]}...")
                success += 1
            else:
                print(f"   ❌ {algo.upper()}: Failed")
        except Exception as e:
            print(f"   ❌ {algo.upper()}: {e}")
    
    return success == len(algorithms)

def test_parallel_tasks():
    """Тест параллельных задач"""
    print("⚡ Тестирование параллельных задач...")
    
    try:
        # Создаем несколько простых задач
        tasks = []
        passwords = ["a", "b", "c"]
        
        for password in passwords:
            # Получаем хеш
            response = requests.get(f"http://localhost:8000/api/bruteforce/demo-hash/{password}", timeout=5)
            target_hash = response.json()['hash']
            
            # Запускаем задачу
            task_data = {
                "hash_type": "md5",
                "target_hash": target_hash,
                "max_length": 1
            }
            response = requests.post("http://localhost:8000/api/bruteforce/start", json=task_data, timeout=5)
            task_id = response.json()['task_id']
            tasks.append((password, task_id))
            print(f"   📤 Task '{password}': {task_id[:8]}...")
        
        # Проверяем активные задачи
        response = requests.get("http://localhost:8000/api/bruteforce/active-tasks", timeout=5)
        active_count = response.json()['count']
        print(f"   ⚡ Active tasks: {active_count}")
        
        return len(tasks) > 0
        
    except Exception as e:
        print(f"   ❌ Parallel tasks error: {e}")
        return False

def test_performance():
    """Простой тест производительности"""
    print("🚄 Тестирование производительности...")
    
    try:
        start_time = time.time()
        
        # Создаем задачу средней сложности
        response = requests.get("http://localhost:8000/api/bruteforce/demo-hash/ab", timeout=5)
        target_hash = response.json()['hash']
        
        task_data = {
            "hash_type": "md5",
            "target_hash": target_hash,
            "max_length": 2
        }
        
        response = requests.post("http://localhost:8000/api/bruteforce/start", json=task_data, timeout=5)
        task_id = response.json()['task_id']
        
        # Ждем завершения (максимум 30 секунд)
        for i in range(30):
            response = requests.get(f"http://localhost:8000/api/bruteforce/task/{task_id}", timeout=5)
            task = response.json()
            
            if task['status'] == 'COMPLETED':
                elapsed = time.time() - start_time
                print(f"   ✅ Found '{task['result']}' in {elapsed:.2f} seconds")
                return True
            elif task['status'] == 'FAILED':
                print(f"   ❌ Task failed: {task.get('result', 'Unknown error')}")
                return False
            
            time.sleep(1)
        
        print("   ⏱️ Task timeout (30s)")
        return False
        
    except Exception as e:
        print(f"   ❌ Performance test error: {e}")
        return False

def check_server():
    """Проверка, что сервер запущен"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 === АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ ЛАБОРАТОРНОЙ РАБОТЫ №3 ===")
    print("📋 Вариант 5: Брутфорс с WebSocket уведомлениями")
    print("=" * 60)
    
    # Проверка сервера
    if not check_server():
        print("❌ Сервер не запущен!")
        print("💡 Запустите: python main.py")
        return
    
    print("✅ Сервер доступен")
    
    # Запуск тестов
    tests = [
        ("REST API", test_api),
        ("WebSocket", test_websocket),
        ("Алгоритмы", test_algorithms),
        ("Параллельные задачи", test_parallel_tasks),
        ("Производительность", test_performance),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Critical error: {e}")
            results.append((test_name, False))
    
    # Итоги
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Прошло тестов: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("🏆 Лабораторная работа готова к сдаче!")
    else:
        print("⚠️ Некоторые тесты провалились")
        print("🔧 Проверьте сервер и зависимости")

if __name__ == "__main__":
    # Проверяем зависимости
    try:
        import requests
        import websocket
    except ImportError as e:
        print(f"❌ Отсутствуют зависимости: {e}")
        print("📦 Установите: pip install requests websocket-client")
        exit(1)
    
    main() 