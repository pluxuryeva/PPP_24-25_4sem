#!/usr/bin/env python3
"""
Консольный клиент для работы с Bruteforce API
Поддерживает REST API запросы и WebSocket соединения
"""

import asyncio
import json
import sys
import threading
from typing import Optional
import websockets
import httpx
import hashlib


class BruteforceClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws")
        self.websocket_tasks = {}
        
    async def create_demo_hash(self, password: str, hash_type: str = "md5") -> str:
        """Создает демонстрационный хеш для тестирования"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/bruteforce/demo-hash/{password}?hash_type={hash_type}")
            if response.status_code == 200:
                data = response.json()
                print(f"Пароль: {data['password']}")
                print(f"Тип хеша: {data['hash_type']}")
                print(f"Хеш: {data['hash']}")
                return data['hash']
            else:
                print(f"Ошибка: {response.text}")
                return ""

    async def start_bruteforce(self, hash_type: str, target_hash: str, charset: str = None, max_length: int = 6) -> Optional[str]:
        """Запускает задачу брутфорса"""
        data = {
            "hash_type": hash_type,
            "target_hash": target_hash,
            "max_length": max_length
        }
        if charset:
            data["charset"] = charset
            
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/bruteforce/start", json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"Задача запущена: {result['task_id']}")
                print(f"Сообщение: {result['message']}")
                return result['task_id']
            else:
                print(f"Ошибка: {response.text}")
                return None

    async def get_task_status(self, task_id: str):
        """Получает статус задачи"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/bruteforce/task/{task_id}")
            if response.status_code == 200:
                data = response.json()
                print(f"Задача: {data['task_id']}")
                print(f"Статус: {data['status']}")
                print(f"Прогресс: {data['progress']}%")
                if data['current_combination']:
                    print(f"Текущая комбинация: {data['current_combination']}")
                if data['combinations_per_second']:
                    print(f"Комбинаций в секунду: {data['combinations_per_second']}")
                if data['result']:
                    print(f"Результат: {data['result']}")
                if data['elapsed_time']:
                    print(f"Время выполнения: {data['elapsed_time']}")
            else:
                print(f"Ошибка: {response.text}")

    async def get_all_tasks(self):
        """Получает все задачи пользователя"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/bruteforce/tasks")
            if response.status_code == 200:
                tasks = response.json()
                if not tasks:
                    print("Нет активных задач")
                    return
                    
                print(f"Найдено задач: {len(tasks)}")
                for task in tasks:
                    print(f"\nЗадача: {task['task_id']}")
                    print(f"  Статус: {task['status']}")
                    print(f"  Тип хеша: {task['hash_type']}")
                    print(f"  Прогресс: {task['progress']}%")
                    if task['result']:
                        print(f"  Результат: {task['result']}")
            else:
                print(f"Ошибка: {response.text}")

    async def listen_websocket(self, task_id: str):
        """Подключается к WebSocket для прослушивания уведомлений"""
        uri = f"{self.ws_url}/ws/{task_id}"
        try:
            print(f"Подключение к WebSocket: {uri}")
            async with websockets.connect(uri) as websocket:
                print(f"WebSocket подключен для задачи {task_id}")
                
                # Отправляем ping для поддержания соединения
                await websocket.send("ping")
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        print(f"\n[{task_id}] {data['status']}")
                        
                        if data['status'] == 'STARTED':
                            print(f"  Тип хеша: {data.get('hash_type', 'N/A')}")
                            print(f"  Размер алфавита: {data.get('charset_length', 'N/A')}")
                            print(f"  Максимальная длина: {data.get('max_length', 'N/A')}")
                            
                        elif data['status'] == 'PROGRESS':
                            print(f"  Прогресс: {data.get('progress', 0)}%")
                            print(f"  Текущая комбинация: {data.get('current_combination', 'N/A')}")
                            print(f"  Комбинаций в секунду: {data.get('combinations_per_second', 0)}")
                            
                        elif data['status'] == 'COMPLETED':
                            print(f"  Результат: {data.get('result', 'Не найден')}")
                            print(f"  Время выполнения: {data.get('elapsed_time', 'N/A')}")
                            break
                            
                        elif data['status'] == 'FAILED':
                            print(f"  Ошибка: {data.get('result', 'Неизвестная ошибка')}")
                            break
                            
                    except json.JSONDecodeError:
                        print(f"Получено: {message}")
                        
        except Exception as e:
            print(f"Ошибка WebSocket соединения: {e}")

    def start_websocket_listener(self, task_id: str):
        """Запускает WebSocket слушатель в отдельном потоке"""
        def run_websocket():
            asyncio.run(self.listen_websocket(task_id))
        
        thread = threading.Thread(target=run_websocket, daemon=True)
        thread.start()
        return thread

    async def interactive_mode(self):
        """Интерактивный режим работы"""
        print("=== Bruteforce Client ===")
        print("Доступные команды:")
        print("1. demo <пароль> [тип_хеша] - создать демо хеш")
        print("2. start <тип_хеша> <хеш> [charset] [max_length] - запустить брутфорс")
        print("3. status <task_id> - получить статус задачи")
        print("4. tasks - показать все задачи")
        print("5. listen <task_id> - подключиться к WebSocket")
        print("6. quick <пароль> - быстрый тест (demo + start + listen)")
        print("7. exit - выход")
        print()
        
        active_listeners = []
        
        while True:
            try:
                command = input("> ").strip().split()
                if not command:
                    continue
                    
                cmd = command[0].lower()
                
                if cmd == "exit":
                    break
                    
                elif cmd == "demo":
                    if len(command) < 2:
                        print("Использование: demo <пароль> [тип_хеша]")
                        continue
                    password = command[1]
                    hash_type = command[2] if len(command) > 2 else "md5"
                    await self.create_demo_hash(password, hash_type)
                    
                elif cmd == "start":
                    if len(command) < 3:
                        print("Использование: start <тип_хеша> <хеш> [charset] [max_length]")
                        continue
                    hash_type = command[1]
                    target_hash = command[2]
                    charset = command[3] if len(command) > 3 else None
                    max_length = int(command[4]) if len(command) > 4 else 6
                    
                    task_id = await self.start_bruteforce(hash_type, target_hash, charset, max_length)
                    if task_id:
                        print("Хотите подключиться к WebSocket для отслеживания? (y/n)")
                        if input().lower().startswith('y'):
                            listener = self.start_websocket_listener(task_id)
                            active_listeners.append(listener)
                    
                elif cmd == "status":
                    if len(command) < 2:
                        print("Использование: status <task_id>")
                        continue
                    await self.get_task_status(command[1])
                    
                elif cmd == "tasks":
                    await self.get_all_tasks()
                    
                elif cmd == "listen":
                    if len(command) < 2:
                        print("Использование: listen <task_id>")
                        continue
                    listener = self.start_websocket_listener(command[1])
                    active_listeners.append(listener)
                    print("WebSocket слушатель запущен в фоне")
                    
                elif cmd == "quick":
                    if len(command) < 2:
                        print("Использование: quick <пароль>")
                        continue
                    password = command[1]
                    
                    # Создаем хеш
                    print("1. Создание демо хеша...")
                    target_hash = await self.create_demo_hash(password, "md5")
                    if not target_hash:
                        continue
                    
                    # Запускаем брутфорс
                    print("\n2. Запуск брутфорса...")
                    charset = "abcdefghijklmnopqrstuvwxyz"  # Простой набор для быстрого теста
                    task_id = await self.start_bruteforce("md5", target_hash, charset, len(password))
                    
                    if task_id:
                        print("\n3. Подключение к WebSocket...")
                        listener = self.start_websocket_listener(task_id)
                        active_listeners.append(listener)
                        print("Отслеживание запущено. Нажмите Enter для продолжения или используйте другие команды.")
                    
                else:
                    print("Неизвестная команда. Введите 'exit' для выхода.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Ошибка: {e}")
        
        print("Завершение работы...")


async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--script":
        # Режим выполнения скрипта
        if len(sys.argv) < 3:
            print("Использование: python client.py --script <файл_скрипта>")
            return
        
        # Здесь можно добавить логику выполнения команд из файла
        script_file = sys.argv[2]
        print(f"Выполнение скрипта: {script_file}")
        # TODO: Реализовать чтение и выполнение команд из файла
    else:
        # Интерактивный режим
        client = BruteforceClient()
        await client.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main()) 