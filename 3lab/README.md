# Bruteforce API с WebSocket уведомлениями

Лабораторная работа по реализации системы брутфорс атак с поддержкой REST API и WebSocket уведомлений в реальном времени.

## Возможности

- REST API для запуска и управления задачами брутфорса
- WebSocket соединения для получения уведомлений в реальном времени
- Поддержка различных типов хешей (MD5, SHA1, SHA256, SHA512)
- Асинхронная обработка задач с помощью Celery
- Консольный клиент для взаимодействия с API
- База данных SQLite для хранения истории задач

## Структура проекта

```
3lab/
├── main.py                 # Основное приложение FastAPI
├── client.py              # Консольный клиент
├── worker.py              # Скрипт для запуска Celery worker
├── requirements.txt       # Зависимости
├── app/
│   ├── api/              # REST API эндпоинты
│   ├── celery/           # Конфигурация и задачи Celery
│   ├── core/             # Конфигурация приложения
│   ├── cruds/            # CRUD операции для БД
│   ├── db/               # Настройка базы данных
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес логика
│   └── websocket/        # WebSocket менеджер
```

## Установка

1. Клонируйте репозиторий и перейдите в директорию проекта
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск

### 1. Запуск FastAPI сервера

```bash
python main.py
```

Сервер будет доступен по адресу: http://localhost:8000

### 2. Запуск Celery worker (в отдельном терминале)

```bash
celery -A app.celery.celery_app worker --loglevel=info
```

Или с помощью скрипта:
```bash
python worker.py
```

### 3. Запуск консольного клиента

```bash
python client.py
```

## API Endpoints

### REST API

- `POST /api/bruteforce/start` - Запуск новой задачи брутфорса
- `GET /api/bruteforce/tasks` - Получить список задач
- `GET /api/bruteforce/task/{task_id}` - Получить статус задачи
- `GET /api/bruteforce/demo-hash/{password}` - Создать демо хеш для тестирования

### WebSocket

- `ws://localhost:8000/ws/{task_id}` - Подключение к конкретной задаче
- `ws://localhost:8000/ws/user/{user_id}` - Подключение к пользователю

## Использование клиента

Консольный клиент поддерживает следующие команды:

- `demo <пароль> [тип_хеша]` - создать демо хеш
- `start <тип_хеша> <хеш> [charset] [max_length]` - запустить брутфорс
- `status <task_id>` - получить статус задачи
- `tasks` - показать все задачи
- `listen <task_id>` - подключиться к WebSocket
- `quick <пароль>` - быстрый тест (demo + start + listen)
- `exit` - выход

### Пример использования

```bash
python client.py
> demo test
> quick abc
> tasks
> exit
```

## Тестирование

Для быстрого тестирования используйте команду `quick` в клиенте:

```bash
> quick test
```

Это создаст хеш MD5 для пароля "test", запустит брутфорс и подключится к WebSocket для отслеживания прогресса.

## Конфигурация

Настройки приложения можно изменить в файле `app/core/config.py`:

- `max_password_length` - максимальная длина пароля (по умолчанию 8)
- `default_charset` - набор символов по умолчанию
- `database_url` - URL базы данных
- `celery_broker_url` - URL брокера Celery

## Примечания

- Для продакшена следует использовать настоящий Redis вместо redislite
- В реальном приложении необходимо добавить аутентификацию
- Ограничение времени выполнения задачи - 10 минут
- Прогресс обновляется каждые 1000 попыток 