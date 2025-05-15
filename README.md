Описание проекта
Это FastAPI приложение для управления пользователями с аутентификацией JWT. Оно предоставляет RESTful API для:

Регистрации новых пользователей

Аутентификации (получения токена)

Получения информации о пользователях

Управления учетными записями

Технологический стек
Python 3.10+

FastAPI - веб-фреймворк

SQLAlchemy - ORM для работы с базой данных

Pydantic - валидация данных

JWT - аутентификация

MySQL - база данных (можно заменить на другую)

Требования
Python 3.10+

MySQL сервер (или другая СУБД)

Установленные зависимости (см. раздел "Установка")

Установка
Клонируйте репозиторий:

bash
git clone https://github.com/your-repo/user-management-api.git
cd user-management-api
Создайте виртуальное окружение:

bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
Установите зависимости:

bash
pip install -r requirements.txt
Создайте файл .env в корне проекта:

ini
DATABASE_URL=mysql+pymysql://username:password@localhost/db_name
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
Запуск приложения
Для разработки:

bash
uvicorn main:app --reload
Для production:

bash
uvicorn main:app --host 0.0.0.0 --port 8000
Приложение будет доступно по адресу: http://localhost:8000