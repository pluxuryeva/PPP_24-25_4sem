# Брутфорс API

API для брутфорс-атаки на хеши паролей (вариант 5 лабораторной работы).

## Функциональность

- Регистрация и авторизация пользователей
- Запуск задач брутфорса с указанием хеша, набора символов и максимальной длины пароля
- Отслеживание статуса выполнения задач
- Получение результатов брутфорс-атаки

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения, отредактировав файл `.env`

4. Выполните миграции базы данных:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Запуск

```bash
python main.py
```

API будет доступно по адресу: http://localhost:8000

## Документация API

После запуска приложения, документация Swagger будет доступна по адресу:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Основные эндпоинты

### Авторизация

- `/sign-up/` - Регистрация нового пользователя
- `/login/` - Вход в систему
- `/users/me/` - Получение информации о текущем пользователе

### Брутфорс

- `/brut_hash` - Запуск задачи брутфорса
- `/get_status` - Получение статуса задачи брутфорса 