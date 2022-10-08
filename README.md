[status badge](https://github.com/mspitsyn/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# Foodgram - «Продуктовый помощник»

Это онлайн-сервис и API для него, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

#### Пример развернутого проекта можно посмотреть [здесь](http://)

# Технологии:
    Django==3.2
    Django-rest-framework==3.12
    Python==3.7.9
    PostgreSQL
    Docker

# Особенности
Проект запускается в четырёх контейнерах [docker-compose](https://docs.docker.com/compose/install/)

IMAGES            | NAMES             | DESCRIPTIONS
------------------|-------------------|--------------------------------------------
nginx:1.19.3      | infra_nginx_1     | контейнер HTTP-сервера
postgres:12.4     | infra_db_1        | контейнер базы данных на PostgreSQL
foodgram_backend  | infra_web_1       | контейнер backend-части Django приложения
foodgram_frontend | infra_frontend_1  | контейнер frontend-части проекта JS-React


# Запуск и работа с проектом
Чтобы развернуть проект, вам потребуется:
1) Клонируем репозиторий GitHub:
```python
git clone git@github.com:mspitsyn/foodgram-project-react.git
```
2) Подключаемся к серверу
```
ssh <server user>@<public server IP>
```
3) Устанавливаем докер на сервер
```
sudo apt install docker.io
```
4) Устанавливаем Docker-Compose (для Linux)
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
5) Получаем права для docker-compose
```
sudo chmod +x /usr/local/bin/docker-compose
```
6) Копируем файлы docker-compose.yaml и nginx.conf на сервер, сделать это можно командой (в случае удаленного запуска)
```
scp docker-compose.yaml <username>@<public ip adress>:/home/<username>/docker-compose.yaml
```
7) Создайте .env файл в директории backend/foodgram/, в котором должны содержаться следующие переменные:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres (по умолчанию)
POSTGRES_USER=postgres (по умолчанию)
POSTGRES_PASSWORD=postgres (по умолчанию)
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=<секретный ключ приложения django>
DEBUG=False
```
Вы можете сгенерировать ```DJANGO_SECRET_KEY``` следующим образом. 
Из директории проекта _/backend/_ выполнить поочередно следующие команды:
```python
python manage.py shell
from django.core.management import utils 
print(utils.get_random_secret_key())
```
Полученный ключ скопировать в ```.env```.

9) Собрать контейнеры:
```python
cd foodgram-project-react/infra
docker-compose up -d --build
```

10) Сделать миграции, собрать статику и создать суперпользователя:
```python
docker-compose exec -T web python manage.py makemigrations users --noinput
docker-compose exec -T web python manage.py makemigrations recipes --noinput
docker-compose exec -T web python manage.py migrate --noinput
docker-compose exec -T web python manage.py collectstatic --no-input
docker-compose exec web python manage.py createsuperuser
```

Чтобы заполнить базу данных начальными данными списка ингридиетов выполните:
```python
docker-compose exec -T web python manage.py loaddata data/ingredients.json
```
Теперь можно зайти в админку _http://<ваш хост>/admin/_ под вашим логином администратора.

## Регистрация и авторизация
В сервисе предусмотрена система регистрации и авторизации пользователей.
Обязательные поля для пользователя:
<li> Логин
<li> Пароль
<li> Email
<li> Имя
<li> Фамилия

## Права доступа к ресурсам сервиса

### неавторизованные пользователи могут:

    - создать аккаунт;
    - просматривать рецепты на главной;
    - просматривать отдельные страницы рецептов;
    - фильтровать рецепты по тегам;

### авторизованные пользователи могут:

    - входить в систему под своим логином и паролем;
    - выходить из системы (разлогиниваться);
    - менять свой пароль;
    - создавать/редактировать/удалять собственные рецепты;
    - просматривать рецепты на главной;
    - просматривать страницы пользователей;
    - просматривать отдельные страницы рецептов;
    - фильтровать рецепты по тегам;
    - работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов;
    - работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл со количеством необходимых ингридиентов для рецептов из списка покупок;
    - подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок;

### администратор
Администратор обладает всеми правами авторизованного пользователя.
<br> Плюс к этому он может:

    - изменять пароль любого пользователя;
    - создавать/блокировать/удалять аккаунты пользователей;
    - редактировать/удалять любые рецепты;
    - добавлять/удалять/редактировать ингредиенты;
    - добавлять/удалять/редактировать теги.


# Ресурсы сервиса

### Рецепт
Рецепт описывается полями:
    Автор публикации (пользователь).
    Название рецепта.
    Картинка рецепта.
    Текстовое описание.
    Ингредиенты: продукты для приготовления блюда по рецепту с указанием количества и единиц измерения.
    Тег.
    Время приготовления в минутах.

### Тег
Тег описывается полями:
    Название.
    Цветовой HEX-код.
    Slug.

### Ингредиент
Ингредиент описывается полями:
    Название.
    Количество (только для рецепта).
    Единицы измерения.

### Список покупок.
Список покупок скачивается в текстовом формате: shopping_cart.txt.

## Фильтрация по тегам
При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводится по нескольким тегам в комбинации «или»: если выбраны несколько тегов — в результате должны быть показаны рецепты, которые отмечены хотя бы одним из этих тегов.
При фильтрации на странице пользователя фильтруются только рецепты выбранного пользователя. Такой же принцип соблюдается при фильтрации списка избранного.

# Примеры запросов к API.

Запросы к API начинаются с «/api/v1/»

1) регистрация пользователя

POST-запрос: /api/users/
<br /> *Request sample:*
```python
{

    "email": "string",
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "password": "string"

}
```
*Response sample (201):*
```python
{

    "email": "string",
    "id": 0,
    "username": "string",
    "first_name": "string",
    "last_name": "string"

}
```
*Response sample (400):*
```python
{
    «field_name»: [
      «Обязательное поле.»
    ]
}
```

2) Получение токена

POST-запрос: /api/auth/token/login/
<br /> *Request sample:*
```python
{
    «email»: «string»,
    «password»: «string»
}
```
*Response sample (201):*
```python
{
    «token»: «string»
}
```
*Response sample (400):*
```python
{
    «field_name»: [
      «string»
    ]
}
```
При развернутом проекте спецификация API доступна локально http://127.0.0.1/api/docs/ или на вашем хосте.

---
### Автор
[Спицын Максим](https://github.com/mspitsyn)