# Cервис Foodgram 

## Описание

Онлайн-сервис Foodgram и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин скачивать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Доступный функционал

- Аутентификация реализована с помощью стандартного модуля DRF - Authtoken.
- У неаутентифицированных пользователей доступ к API только на уровне чтения.
- Создание объектов разрешено только зарегистрированным пользователям.
- Управление пользователями.
- Возможность получения подробной информации о себе и ее редактирование.
- Возможность подписаться на других пользователей и отписаться от них.
- Получение списка всех тегов и ингредиентов.
- Получение списка всех рецептов, их добавление.Получение, обновление и удаление конкретного рецепта.
- Возможность добавить рецепт в избранное.
- Возможность добавить рецепт в список покупок.
- Возможность скачать список покупок в PDF формате.
- Фильтрация по полям.

#### Документация к API доступна по адресу <http://localhost/api/docs/> после локального запуска проекта

#### Технологи

- Python 3.9
- Django 3.2.6
- Django Rest Framework 3.12.4
- Authtoken
- Docker
- Docker-compose
- PostgreSQL
- Gunicorn
- Nginx
- GitHub Actions

#### Локальный запуск проекта

- Склонировать репозиторий:

```bash
   git clone <название репозитория>
```

```bash
   cd <название репозитория> 
```

Cоздать и активировать виртуальное окружение:

Команда для установки виртуального окружения на Mac или Linux:

```bash
   python3 -m venv env
   source env/bin/activate
```

Команда для Windows:

```bash
   python -m venv venv
   source venv/Scripts/activate
```

- Перейти в директорию infra:

```bash
   cd infra
```

- Создать файл .env по образцу:

```bash
   cp .env.example .env
```

- Выполнить команду для доступа к документации:

```bash
   docker-compose up 
```

Установить зависимости из файла requirements.txt:

```bash
   cd ..
   cd backend
   pip install -r requirements.txt
```

```bash
   python manage.py migrate
```

Заполнить базу тестовыми данными об ингредиентах:

```bash
   python manage.py load_ingredients
```

Создать суперпользователя, если необходимо:

```bash
python manage.py createsuperuser
```

- Запустить локальный сервер:

```bash
   python manage.py runserver
```


### Инструкция для разворачивания проекта на удаленном сервере:

- Склонируйте проект из репозитория:

```sh
$ git clone https://github.com/MrKlejtont/foodgram-project-react.git
```

- Выполните вход на удаленный сервер

- Установите DOCKER на сервер:
```sh
apt install docker.io 
```

- Установитe docker-compose на сервер:
```sh
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

- Отредактируйте конфигурацию сервера NGNIX:
```sh
Локально измените файл ..infra/nginx.conf - замените данные в строке server_name на IP-адрес удаленного сервера
```

- Скопируйте файлы docker-compose.yml и nginx.conf из директории ../infra/ на удаленный сервер:
```sh
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yaml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
- Создайте переменные окружения (указаны в файле ../infra/.env)

- Установите и активируйте виртуальное окружение (для Windows):

```sh
python -m venv venv 
source venv/Scripts/activate
python -m pip install --upgrade pip
``` 

- Запустите приложение в контейнерах:

```sh
docker-compose up -d --build
```

- Выполните миграции:

```sh
docker-compose exec backend python manage.py migrate
```

- Создайте суперпользователя:

```sh
docker-compose exec backend python manage.py createsuperuser
```

- Выполните команду для сбора статики:

```sh
docker-compose exec backend python manage.py collectstatic --no-input
```

- Команда для заполнения тестовыми данными:
```sh
docker-compose exec backend python manage.py load_ingredients
```

- Команда для остановки приложения в контейнерах:

```sh
docker-compose down -v
```

#### Примеры некоторых запросов API

Регистрация пользователя:

```bash
   POST /api/v1/users/
```

Получение данных своей учетной записи:

```bash
   GET /api/v1/users/me/ 
```

Добавление подписки:

```bash
   POST /api/v1/users/id/subscription/
```

Обновление рецепта:
  
```bash
   PATCH /api/v1/recipes/id/
```

Удаление рецепта из избранного:

```bash
   DELETE /api/v1/recipes/id/favorite/
```

Получение списка ингредиентов:

```bash
   GET /api/v1/ingredients/
```

Скачать список покупок:

```bash
   GET /api/v1/recipes/download_shopping_cart/
```

#### Полный список запросов API находятся в документации

Проект доступен по адресу: <https://myfoodgram.onthewifi.com/>

#### Автор

Екатерина Ефимова - [https://github.com/MrKlejton](https://github.com/MrKlejton)
