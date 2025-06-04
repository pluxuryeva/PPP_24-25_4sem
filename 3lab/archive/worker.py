#!/usr/bin/env python3
"""
Worker для выполнения фоновых задач
В этой реализации мы используем asyncio вместо Celery
"""

import asyncio
from app.services.task_manager import task_manager

def main():
    print("Воркер для фоновых задач запущен")
    print("Используем встроенный TaskManager с asyncio")
    print("Задачи выполняются автоматически при запуске FastAPI сервера")
    print("Для работы запустите: python main.py")

if __name__ == "__main__":
    main() 