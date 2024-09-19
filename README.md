### Hexlet tests and linter status:
[![Actions Status](https://github.com/sva24/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/sva24/python-project-83/actions)  


### 🔍 Анализатор страниц
Анализатор страниц – это полноценное приложение
на базе фреймворка Flask, которое позволяет
пользователям анализировать веб-страницы и получать информацию о их содержимом,
включая заголовки, метаданные и другое.

## 🔨 Минимальные требования
- Python >= 3.10  
- flask = "^3.0.3"
- gunicorn = "^23.0.0"
- python-dotenv = "^1.0.1"
- psycopg2-binary = "^2.9.9"
- validators = "^0.34.0"
- requests = "^2.32.3"
- beautifulsoup4 = "^4.12.3"

## 🛠️ Установка

1. Установите PostgreSQL:

   sudo apt install postgresql
2. Склонируйте репозиторий:
    
    git clone https://github.com/sva24/python-project-83.git  
    cd python-project-83

3. Перед запуском приложения добавьте авторизационные данные в файл .env:
    
    nano .env

    SECRET_KEY: Секретный ключ для Flask приложения.
    DATABASE_URL: Строка подключения к БД вида postgresql://user:password@host:port/database_name.

4. Установите зависимости и соберите проект:

    make install  
    make build   

## 🌟 Пример работы проекта

Вы можете ознакомиться с работой проекта по следующей ссылке:

[👉 Перейти к проекту](https://python-project-83-th93.onrender.com)
