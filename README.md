# FastAPI Microservices Project

**GitHub:** https://github.com/SeTyr24/FastAPI

Проект состоит из двух микросервисов на базе FastAPI:
1. **ToDo Service** - сервис управления задачами с CRUD-операциями
2. **URL Shortener Service** - сервис сокращения URL-адресов

## Структура проекта

```
.
├── todo_app/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── shorturl_app/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
```

## Клонирование репозитория

```bash
git clone https://github.com/SeTyr24/FastAPI.git
cd FastAPI
```

## Описание сервисов

### ToDo Service

API для управления списком задач с возможностью создания, чтения, обновления и удаления задач.

**Эндпоинты:**
- `POST /items` - создание новой задачи
- `GET /items` - получение списка всех задач
- `GET /items/{item_id}` - получение задачи по ID
- `PUT /items/{item_id}` - обновление задачи по ID
- `DELETE /items/{item_id}` - удаление задачи

**Модель задачи:**
```json
{
  "title": "Название задачи",
  "description": "Описание задачи (опционально)",
  "completed": false
}
```

### URL Shortener Service

Сервис для сокращения длинных URL-адресов и перенаправления по коротким ссылкам.

**Эндпоинты:**
- `POST /shorten` - создание короткой ссылки
- `GET /{short_id}` - перенаправление на полный URL
- `GET /stats/{short_id}` - получение информации о ссылке

**Пример запроса для сокращения URL:**
```json
{
  "url": "https://example.com/very/long/url"
}
```

## Локальный запуск без Docker

### ToDo Service

```bash
cd todo_app
pip install -r requirements.txt
# Для Windows PowerShell:
$env:DB_DIR="./data"; uvicorn main:app --reload --port 8000
# Для Linux/Mac:
# DB_DIR=./data uvicorn main:app --reload --port 8000
```

Доступен по адресу: http://localhost:8000
Документация API: http://localhost:8000/docs

### URL Shortener Service

```bash
cd shorturl_app
pip install -r requirements.txt
# Для Windows PowerShell:
$env:DB_DIR="./data"; uvicorn main:app --reload --port 8001
# Для Linux/Mac:
# DB_DIR=./data uvicorn main:app --reload --port 8001
```

Доступен по адресу: http://localhost:8001
Документация API: http://localhost:8001/docs

## Запуск с Docker

### Предварительные требования

- Docker Desktop установлен и запущен
- Доступ к интернету для загрузки образов

### Создание именованных томов

```bash
docker volume create todo_data
docker volume create shorturl_data
```

### Сборка образов локально

```bash
# ToDo Service
docker build -t todo-service:latest todo_app/

# URL Shortener Service
docker build -t shorturl-service:latest shorturl_app/
```

### Запуск контейнеров

```bash
# ToDo Service на порту 8000
docker run -d -p 8000:80 -v todo_data:/app/data --name todo-service todo-service:latest

# URL Shortener Service на порту 8001
docker run -d -p 8001:80 -v shorturl_data:/app/data --name shorturl-service shorturl-service:latest
```

### Проверка работы

После запуска контейнеров сервисы будут доступны:
- ToDo Service: http://localhost:8000 (документация: http://localhost:8000/docs)
- URL Shortener: http://localhost:8001 (документация: http://localhost:8001/docs)

### Управление контейнерами

```bash
# Просмотр запущенных контейнеров
docker ps

# Остановка контейнеров
docker stop todo-service shorturl-service

# Удаление контейнеров
docker rm todo-service shorturl-service

# Просмотр логов
docker logs todo-service
docker logs shorturl-service

# Перезапуск контейнеров
docker restart todo-service shorturl-service
```

## Загрузка кода на GitHub

### Инициализация репозитория (если еще не сделано)

```bash
git init
git add .
git commit -m "Initial commit: FastAPI microservices with Docker"
git branch -M main
git remote add origin https://github.com/SeTyr24/FastAPI.git
git push -u origin main
```

### Обновление кода

```bash
git add .
git commit -m "Описание изменений"
git push
```

## Публикация на Docker Hub

### 1. Авторизация в Docker Hub

```bash
docker login
```

Введите ваш логин и пароль Docker Hub.

### 2. Тегирование образов

```bash
docker tag todo-service:latest setyr24/todo-service:latest
docker tag shorturl-service:latest setyr24/shorturl-service:latest
```

### 3. Публикация образов

```bash
docker push setyr24/todo-service:latest
docker push setyr24/shorturl-service:latest
```

### 4. Запуск из Docker Hub

После публикации образы можно запустить на любой машине с Docker:

```bash
docker run -d -p 8000:80 -v todo_data:/app/data --name todo-service setyr24/todo-service:latest
docker run -d -p 8001:80 -v shorturl_data:/app/data --name shorturl-service setyr24/shorturl-service:latest
```

## Примеры использования API

### ToDo Service

**Создание задачи:**
```bash
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{"title": "Купить молоко", "description": "В магазине на углу", "completed": false}'
```

**Получение всех задач:**
```bash
curl "http://localhost:8000/items"
```

**Обновление задачи:**
```bash
curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Удаление задачи:**
```bash
curl -X DELETE "http://localhost:8000/items/1"
```

### URL Shortener Service

**Создание короткой ссылки:**
```bash
curl -X POST "http://localhost:8001/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url"}'
```

**Переход по короткой ссылке:**
```bash
# В браузере откройте: http://localhost:8001/{short_id}
# Или через curl:
curl -L "http://localhost:8001/{short_id}"
```

**Получение статистики:**
```bash
curl "http://localhost:8001/stats/{short_id}"
```

## Тестирование сохранения данных

Чтобы убедиться, что данные сохраняются после перезапуска:

1. Создайте несколько задач/ссылок
2. Остановите контейнер: `docker stop todo-service`
3. Запустите контейнер снова: `docker start todo-service`
4. Проверьте, что данные сохранились

## Технологии

- **FastAPI** - современный веб-фреймворк для Python
- **SQLite** - встраиваемая база данных
- **Uvicorn** - ASGI сервер
- **Docker** - контейнеризация приложений
- **Pydantic** - валидация данных

## Лицензия

MIT

## Автор

Создано для демонстрации работы с FastAPI и Docker.
