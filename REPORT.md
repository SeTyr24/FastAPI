# Отчет о реализации проекта FastAPI Microservices

## Дата: 24 декабря 2025

---

##  Задача

Разработать два микросервиса на базе FastAPI:
1. **ToDo-сервис** - управление списком задач (CRUD операции)
2. **Сервис сокращения URL** - создание коротких ссылок и перенаправление

Упаковать оба сервиса в Docker-контейнеры и опубликовать на Docker Hub.

---



### 1. Реализованы оба микросервиса на FastAPI

**ToDo Service:**
- POST /items - создание новой задачи
- GET /items - получение списка всех задач
- GET /items/{item_id} - получение задачи по ID
- PUT /items/{item_id} - обновление задачи
- DELETE /items/{item_id} - удаление задачи
- Автоматическая документация на /docs

**URL Shortener Service:**
- POST /shorten - создание короткой ссылки
- GET /{short_id} - перенаправление по короткой ссылке
- GET /stats/{short_id} - получение информации о ссылке
- Автоматическая документация на /docs

**Файлы реализации:**
- `todo_app/main.py` - 151 строка кода
- `shorturl_app/main.py` - 149 строк кода

---

### 2. Подключён SQLite для хранения данных

**Описание:**
- **ToDo Service**: База `todos.db` (12 KB) с таблицей `todos`
- **URL Shortener**: База `urls.db` (16 KB) с таблицей `urls`

**Особенности:**
- Базы создаются автоматически при первом запуске
- Таблицы создаются автоматически через `init_db()`
- Данные сохраняются между перезапусками контейнеров

**Проверка:**
- Созданы 2 задачи в ToDo Service
- Создана 1 короткая ссылка в URL Shortener
- Контейнер остановлен и перезапущен - данные сохранились 

---

### 3. Написаны Dockerfile для каждого сервиса

**ToDo Service Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
RUN mkdir -p /app/data
VOLUME /app/data
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

**URL Shortener Dockerfile:**
- Идентична конфигурация ToDo Service
- Оба сервиса используют Python 3.11-slim базовый образ
- Оба объявляют VOLUME /app/data для персистентности

**Файлы:**
- `todo_app/Dockerfile`
- `shorturl_app/Dockerfile`

---

### 4. Использованы Docker тома для сохранения данных

**Созданные тома:**
```
DRIVER    VOLUME NAME
local     todo_data
local     shorturl_data
```

**Монтирование в контейнерах:**
- ToDo Service: `-v todo_data:/app/data`
- URL Shortener: `-v shorturl_data:/app/data`

**Проверка персистентности:**
- Контейнер остановлен
- Контейнер перезапущен
- Данные сохранились на томах

---

### 5. Проведено локальное тестирование

**Эндпоинты протестированы:**

**ToDo Service:**
```bash
# POST /items - создание задачи
Status: 201 Created
Response: {"id":1,"title":"Купить продукты",...}

# GET /items - получение всех
Status: 200 OK
Response: [{"id":1,...}, {"id":2,...}]

# GET /items/{item_id} - получение по ID
Status: 200 OK

# PUT /items/{item_id} - обновление
Status: 200 OK

# DELETE /items/{item_id} - удаление
Status: 204 No Content
```

**URL Shortener Service:**
```bash
# POST /shorten - создание ссылки
Status: 201 Created
Response: {"short_id":"4Eytsw","short_url":"/4Eytsw",...}

# GET /stats/{short_id} - статистика
Status: 200 OK
Response: {"short_id":"4Eytsw","full_url":"https://github.com/SeTyr24/FastAPI"}

# GET /{short_id} - редирект
Status: 307 Temporary Redirect
```

**Документация:**
- http://localhost:8000/docs - интерактивная документация ToDo Service
- http://localhost:8001/docs - интерактивная документация URL Shortener

---

### 6. Исходный код загружен на GitHub

**Репозиторий:** https://github.com/SeTyr24/FastAPI

**Содержимое репозитория:**
```
FastAPI/
├── todo_app/
│   ├── main.py           151 строк
│   ├── requirements.txt  
│   └── Dockerfile       
├── shorturl_app/
│   ├── main.py           149 строк
│   ├── requirements.txt  
│   └── Dockerfile       
├── README.md             Подробная документация
├── .gitignore           
└── [Файлы Git]
```

**Коммиты:**
- `d5fb8da` - Initial commit: FastAPI microservices with Docker

**Статус:**
-  Синхронизирован с GitHub
-  Branch: main

---

### 7.  Docker Hub образы опубликованы

**Опубликованные образы:**

1. **ToDo Service**
   - URL: https://hub.docker.com/r/setyr24/todo-service
   - Тег: `setyr24/todo-service:latest`
   - Размер: ~450 MB
   - Статус:  Опубликован

2. **URL Shortener Service**
   - URL: https://hub.docker.com/r/setyr24/shorturl-service
   - Тег: `setyr24/shorturl-service:latest`
   - Размер: ~450 MB
   - Статус: Опубликован

**Команды для запуска:**
```bash
# Создание томов
docker volume create todo_data
docker volume create shorturl_data

# Запуск сервисов
docker run -d -p 8000:80 -v todo_data:/app/data --name todo-service setyr24/todo-service:latest
docker run -d -p 8001:80 -v shorturl_data:/app/data --name shorturl-service setyr24/shorturl-service:latest
```

---

## Итоговая статистика

| Параметр | Значение |
|----------|----------|
| **Микросервисов** | 2 (ToDo + URL Shortener) |
| **Эндпоинтов всего** | 8 |
| **Строк кода** | 300+ |
| **Docker образов** | 2 |
| **Docker томов** | 2 |
| **SQLite баз** | 2 |
| **Тестовых данных** | 3 (2 задачи + 1 ссылка) |
| **Документация** | Swagger UI на /docs |
| **GitHub репозиторий** | https://github.com/SeTyr24/FastAPI |
| **Docker Hub репозиторий** | setyr24/{todo-service, shorturl-service} |

---

## Ссылки на ресурсы

### GitHub
- **Репозиторий:** https://github.com/SeTyr24/FastAPI
- **Код:** Полностью синхронизирован

### Docker Hub
- **ToDo Service:** https://hub.docker.com/r/setyr24/todo-service
- **URL Shortener:** https://hub.docker.com/r/setyr24/shorturl-service

### Локальный запуск
- **ToDo Service API:** http://localhost:8000
- **ToDo Service Docs:** http://localhost:8000/docs
- **URL Shortener API:** http://localhost:8001
- **URL Shortener Docs:** http://localhost:8001/docs

---

## Технологический стек

- **Framework:** FastAPI 0.104.1
- **ASGI Server:** Uvicorn 0.24.0
- **Database:** SQLite 3
- **Validation:** Pydantic 2.5.0
- **Containerization:** Docker
- **Version Control:** Git/GitHub
- **Python:** 3.11
- **Base Image:** python:3.11-slim

---

## Ключевые особенности

1. **Микросервисная архитектура** - каждый сервис независим
2. **Персистентные данные** - использование Docker томов
3. **Автоматическая документация** - Swagger UI на /docs
4. **Полная валидация** - Pydantic models
5. **Обработка ошибок** - HTTPException с правильными кодами
6. **SQLite базы данных** - встраиваемая БД, удобная для контейнеризации
7. **Docker Hub** - образы готовы к использованию на любой машине

---

## Выводы

Проект полностью реализован в соответствии со всеми требованиями:

Оба микросервиса работают корректно
Данные надежно хранятся в SQLite
Docker контейнеры собраны и опубликованы
Код размещен на GitHub
Документация полная и актуальная
Все требования чек-листа выполнены

**Проект готов к использованию и развертыванию на любой машине с Docker.**

---

**Подготовил:** GitHub пользователь @SeTyr24
**Дата отчета:** 24 декабря 2025
