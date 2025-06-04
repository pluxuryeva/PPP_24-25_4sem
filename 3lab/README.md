# Лабораторная работа №3: Асинхронное API с WebSocket и TaskManager

**Вариант 5:** Брутфорс с WebSocket уведомлениями

## 📋 Описание

Данная лабораторная работа расширяет функциональность проекта из лабораторной работы №1, добавляя:

- **WebSocket поддержку** для уведомлений в реальном времени
- **TaskManager** как альтернативу Celery для асинхронных задач
- **Сохранение функциональности REST API** из предыдущих работ

## 🚀 Быстрый запуск

1. **Установка зависимостей:**
```bash
pip install -r requirements.txt
```

2. **Запуск сервера:**
```bash
python main.py
```

3. **Сервер будет доступен:**
- REST API: `http://localhost:8000`
- WebSocket: `ws://localhost:8000/ws/{task_id}`
- Документация API: `http://localhost:8000/docs`

## 🏗️ Структура проекта

```
3lab/
├── app/
│   ├── api/           # REST API endpoints
│   ├── core/          # Конфигурация
│   ├── db/            # База данных SQLite
│   ├── models/        # Модели базы данных
│   ├── cruds/         # CRUD операции
│   ├── schemas/       # Pydantic схемы
│   ├── services/      # TaskManager и бизнес-логика
│   └── websocket/     # WebSocket менеджер
├── main.py            # Точка входа FastAPI
├── requirements.txt   # Зависимости
├── client.py          # Консольный клиент
├── bruteforce.db      # База данных SQLite
└── archive/           # Тестовые файлы
```

## 🔌 WebSocket API

### Подключение
```javascript
ws://localhost:8000/ws/{task_id}
```

### Типы уведомлений

**1. Начало задачи:**
```json
{
  "status": "STARTED",
  "task_id": "unique-task-id",
  "hash_type": "md5",
  "charset_length": 62,
  "max_length": 8
}
```

**2. Прогресс выполнения:**
```json
{
  "status": "PROGRESS",
  "task_id": "unique-task-id",
  "progress": 30,
  "current_combination": "abc",
  "combinations_per_second": 15000
}
```

**3. Завершение задачи:**
```json
{
  "status": "COMPLETED",
  "task_id": "unique-task-id",
  "result": "найденный_пароль",
  "elapsed_time": "00:05:23"
}
```

## 🌐 REST API Endpoints

### Брутфорс

- `POST /api/bruteforce/start` - Запуск новой задачи
- `GET /api/bruteforce/tasks` - Список всех задач
- `GET /api/bruteforce/task/{task_id}` - Статус конкретной задачи
- `DELETE /api/bruteforce/task/{task_id}` - Отмена задачи
- `GET /api/bruteforce/active-tasks` - Активные задачи
- `GET /api/bruteforce/demo-hash/{password}` - Создание демо-хеша

### Пример запроса

```bash
# Создание демо-хеша
curl "http://localhost:8000/api/bruteforce/demo-hash/test"

# Запуск брутфорса
curl -X POST "http://localhost:8000/api/bruteforce/start" \
  -H "Content-Type: application/json" \
  -d '{
    "hash_type": "md5",
    "target_hash": "098f6bcd4621d373cade4e832627b4f6",
    "max_length": 4
  }'
```

## 👨‍💻 Консольный клиент

Запуск интерактивного клиента:
```bash
python client.py
```

### Команды клиента:
- `demo` - Создать демо-хеш
- `bruteforce` - Запустить брутфорс
- `status` - Проверить статус задач
- `monitor` - Мониторинг в реальном времени
- `websocket` - Тест WebSocket подключения
- `help` - Справка
- `exit` - Выход

## 🧪 Тестирование

Все тестовые файлы находятся в папке `archive/`:

- `final_demo.py` - Полная демонстрация функционала
- `quick_test.py` - Быстрый тест работоспособности
- `websocket_working_test.py` - Тест WebSocket с уведомлениями
- `full_test.py` - Комплексное тестирование API

Запуск демонстрации:
```bash
python archive/final_demo.py
```

## ⚡ Особенности реализации

### TaskManager
- **Асинхронное выполнение** задач без Celery
- **WebSocket уведомления** о прогрессе
- **Сохранение состояния** в SQLite
- **Управление активными задачами**

### WebSocket
- **Реальное время** уведомлений
- **Автоматическое переподключение**
- **Поддержка множественных подключений**
- **Обработка отключений**

### База данных
- **SQLite** для простоты развертывания
- **Хранение истории** всех задач
- **Отслеживание прогресса** выполнения

## 🔐 Поддерживаемые алгоритмы

- **MD5** - Быстрое хеширование для тестов
- **SHA1** - Стандартный алгоритм
- **SHA256** - Криптографически стойкий
- **SHA512** - Максимальная безопасность

## 📊 Мониторинг

### Через REST API:
```bash
# Статистика всех задач
curl "http://localhost:8000/api/bruteforce/tasks"

# Активные задачи
curl "http://localhost:8000/api/bruteforce/active-tasks"
```

### Через WebSocket:
Подключитесь к `ws://localhost:8000/ws/{task_id}` для получения уведомлений в реальном времени.

## 🛠️ Требования

- **Python 3.9+**
- **FastAPI** для веб-сервера
- **SQLite** как база данных
- **WebSockets** для уведомлений
- **SQLAlchemy 1.4** для ORM

## 🎯 Соответствие требованиям

✅ **WebSocket поддержка** - Реализована с уведомлениями  
✅ **Альтернатива Celery** - TaskManager с асинхронными задачами  
✅ **Консольный клиент** - Интерактивный режим с командами  
✅ **Сохранение REST API** - Полная совместимость с лаб.работой №1  
✅ **Структура проекта** - Соответствует требованиям  
✅ **Уведомления** - WebSocket сообщения о прогрессе  

## 📝 Лицензия

Лабораторная работа выполнена в рамках учебного курса.

---

**Автор:** Студент группы [ваша группа]  
**Вариант:** 5 - Брутфорс с WebSocket уведомлениями  
**Дата:** $(date) 