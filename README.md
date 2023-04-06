# server ip = 158.160.26.243

# yamdb_final
yamdb_final
[![yamdb_workflow](https://github.com/PostHaineku/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/PostHaineku/yamdb_final/actions/workflows/yamdb_workflow.yml)

# api_yamdb
api_yamdb
## Название:
YaMDB
### Описание:
Проект YaMDb собирает отзывы пользователей на произведения. Произведения делятся на категории. 
На произведение можно добавить ревью с оценкой. К ревью можно оставить комментарий.
#### Технологии:
asgiref==3.3.2
Django==3.2
django-filter==2.4.0
djangorestframework==3.12.4
djangorestframework-simplejwt==4.8.0
gunicorn==20.0.4
psycopg2-binary==2.9.5
PyJWT==2.1.0
pytz==2020.1
sqlparse==0.3.1
pytest==6.2.4
pytest-django==4.4.0
pytest-pythonpath==0.7.3
### Запуск проекта:
Создать контейнер проекта в docker из дериктории с файлом docker-compose
docker-compose up -d --build
Выполнить миграции
docker-compose exec web python manage.py migrate
Создание суперюзера
docker-compose exec web python manage.py createsuperuser
Сбор статики
docker-compose exec web python manage.py collectstatic --no-input
Остановка контейнера
docker-compose down -v
### Загрузка database из csv:
После выполнения миграций загрузите тестовую database командой
```
docker-compose exec web python manage.py load_database
```
### Примеры запросов к api_yamdb:

Аутентификация:
```
http://127.0.0.1:8000/api/v1/auth/signup/
http://127.0.0.1:8000/api/v1/auth/token/
```

Получение списка и добавление жанров:
```
http://127.0.0.1:8000/api/v1/genres/
```

Удаление жанра:
```
http://127.0.0.1:8000/api/v1/genres/{slug}/
```

Добавление произведения:
```
http://127.0.0.1:8000/api/v1/titles/
```

Получение информации о произведении, частичное обновление информации, удаление:
```
http://127.0.0.1:8000/api/v1/titles/{titles_id}/
```

Добавление нового отзыва:
```
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/
```

Полуение отзыва по id, частичное обновление, удаление:
```
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/
```

Получение списка всех комментариев к отзыву, добавление комментария к отзыву:
```
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/
```

Получение комментария к отзыву, частичное обновление комментария, удаление:
```
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
```

Получение списка всех пользователей, добавление нового пользователя, :
```
http://127.0.0.1:8000/api/v1/users/
```

Получение пользователя по username, изменение данных пользователя, удаление:
```
http://127.0.0.1:8000/api/v1/users/{username}/
```

Получение данных своей учетной записи, изменение данных своей учетной записи:
```
http://127.0.0.1:8000/api/v1/users/me/
```
