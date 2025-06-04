#!/usr/bin/env python3
"""
Скрипт для запуска Celery worker
"""

from app.celery.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start() 