# Nutrition Tracker

Учебный Django-проект для учета питания, продуктов, рецептов и социальной активности пользователей.

## Стек

- Python 3.9+
- Django 6.0
- SQLite


## Запуск проекта

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Что реализовано

- Лента рецептов на главной странице (свои + друзей) с пагинацией.
- Поиск продуктов и API для продуктов/рецептов.
- Социальная часть: друзья и заявки.

## Деплой на Render (бесплатный тариф)

Проект подготовлен к деплою:
- `requirements.txt`
- `Procfile`
- `render.yaml`
- переменные окружения в `settings.py` (`DEBUG`, `ALLOWED_HOSTS`, `DJANGO_SECRET_KEY`, `DATABASE_URL`)

После первого деплоя на Render нужно выполнить:

```bash
python manage.py migrate
python manage.py createsuperuser
```

## CI/CD

Добавлен GitHub Actions workflow: `.github/workflows/ci.yml`

Он запускает:
- `python manage.py check`
- `python manage.py migrate`
- `python manage.py test`

## Распределение по веткам

- `main` или `master` — общий стабильный код
- `feature/users` — регистрация, логин, профиль, друзья (Гуртов)
- `feature/diary` — продукты, дневник питания, калории (Петриков)
- `feature/recipes` — рецепты, ингредиенты, API (Седых)



