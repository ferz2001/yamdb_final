### Описание

```
Проект **YaMDb** собирает отзывы пользователей на различные произведения.
```

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/kmilobendzky/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Подготовить и выполнить миграции:

```
python3 manage.py makemigrations
```

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Описание API

  запросы к API начинаются с `/api/v1/`
  формат POST, PATCH запросов - JSON

    # Алгоритм регистрации пользователей
    1. Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами `email` и `username` на эндпоинт `/api/v1/auth/signup/`.
    2. **YaMDB** отправляет письмо с кодом подтверждения (`confirmation_code`) на адрес  `email`.
    3. Пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/`, в ответе на запрос ему приходит `token` (JWT-токен).
    4. При желании пользователь отправляет PATCH-запрос на эндпоинт `/api/v1/users/me/` и заполняет поля в своём профайле (описание полей — в документации).

    # Аутентификация
    Используется аутентификация с использованием JWT-токенов с предшествующим name: Bearer
    Пример: Bearer -=q0t-0ik,-05914r§0i

## paths:

  /auth/signup/:
  
    Регистрация нового пользователя. Получаем код подтверждения на переданный `email`.
      Права доступа: **Доступно без токена.**
      Использовать имя 'me' в качестве `username` запрещено.
      Поля `email` и `username` должны быть уникальными.
      Metod: POST
        required:
          - email
          - username

  /auth/token/:
  
    Получение JWT-токена. Получение JWT-токена в обмен на `username` и `confirmation code`.
      Права доступа: **Доступно без токена.**
      Metod: POST
        required:
          - username
          - confirmation_code

  /categories/:

    Получение списка всех категорий.
      Права доступа: **Доступно без токена**
      Metod: GET
        parameters:
        - name: search
          description: Поиск по названию категории

    Добавление новой категории.
      Права доступа: **Администратор.** | security: - jwt-token.
      Поле `slug` каждой категории должно быть уникальным.
      Metod: POST
        required:
          - name
          - slug

  /categories/{slug}/:
  
    Удаление категории.
      Права доступа: **Администратор.** | security: - jwt-token.
      Metod: DELETE
        parameters:
        - name: slug

  /genres/:

    Получение списка всех жанров.
      Права доступа: **Доступно без токена**
      Metod: GET
        parameters:
        - name: search
          description: Поиск по названию жанров

    Добавление новой категории.
      Права доступа: **Администратор.** | security: - jwt-token.
      Поле `slug` каждого жанра должно быть уникальным.
      Metod: POST
        required:
          - name
          - slug

  /genres/{slug}/:

    Удаление жанра.
      Права доступа: **Администратор.** | security: - jwt-token.
      Metod: DELETE
        parameters:
        - name: slug

  /titles/:

    Получение списка всех произведений.
      Права доступа: **Доступно без токена**
      Metod: GET
        parameters:
          - name: category
            description: фильтрует по полю slug категории
          - name: genre
            description: фильтрует по полю slug жанра
          - name: name
            description: фильтрует по части названию произведения
          - name: year
            description: фильтрует по году

    Добавление нового произведения.
      Права доступа: **Администратор.** | security: - jwt-token.
      Нельзя добавлять произведения, которые еще не вышли (год выпуска не может быть больше текущего).
      При добавлении нового произведения требуется указать уже существующие категорию и жанр.
      Metod: POST
        required:
          - name
          - year
          - genre (список slug нескольких жанров)
          - category (slug категории)
        not required:
          - description

  /titles/{titles_id}/:
  
    Получение информации о произведении.
      Права доступа: **Доступно без токена**
      Metod: GET
        parameters:
          - name: titles_id

    Частичное обновление информации о произведении.
      Права доступа: **Администратор** | security: - jwt-token.
      Metod: PATCH
        not required:
          - name
          - year
          - description
          - genre (список slug нескольких жанров)
          - category (slug категории)

    Удаление произведения.
      Права доступа: **Администратор** | security: - jwt-token.
      Metod: DELETE
        parameters:
        - name: titles_id

  /titles/{title_id}/reviews/:
  
    Получение списка всех отзывов.
      Права доступа: **Доступно без токена**.
      Metod: GET
        parameters:
          - name: title_id

    Добавление нового отзыва.
      Права доступа: **Аутентифицированные пользователи.** | security: - jwt-token.
      Пользователь может оставить только один отзыв на произведение.
      Metod: POST
        parameters:
          - name: titles_id
        required:
          - text
          - score (оценка произведения от 1 до 10)

  /titles/{title_id}/reviews/{review_id}/:
  
    Получить отзыв по id для указанного произведения.
      Права доступа: **Доступно без токена.**
      Metod: GET
        parameters:
          - name: title_id
          - name: review_id

    Частичное обновление отзыва по id.
      Права доступа: **Автор отзыва, модератор или администратор.** | security: - jwt-token.
      Metod: PATCH
        not required:
          - text
          - score (оценка произведения от 1 до 10)

    Удаление отзыва по id.
       Права доступа: **Автор отзыва, модератор или администратор.** | security: - jwt-token.
       Metod: DELETE
        parameters:
          - name: titles_id
          - name: review_id

  /titles/{title_id}/reviews/{review_id}/comments/:
  
    Получить список всех комментариев к отзыву по id.
      Права доступа: **Доступно без токена.**
      Metod: GET
        parameters:
          - name: title_id
          - name: review_id

    Добавление комментария к отзыву.
      Права доступа: **Аутентифицированные пользователи.** | security: - jwt-token.
      Metod: POST
        parameters:
          - name: title_id
          - name: review_id
        required:
          - text


  /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/:
  
    Получить комментарий для отзыва по id.
      Права доступа: **Доступно без токена.**
      Metod: GET
        parameters:
          - name: title_id
          - name: review_id
           - name: comment_id

    Частично обновить комментарий к отзыву по id.
      Права доступа: **Автор комментария, модератор или администратор**. | security: - jwt-token.
      Metod: PATCH
        parameters:
          - name: title_id
          - name: review_id
           - name: comment_id
        required:
          - text

    Удалить комментарий к отзыву по id.
      Права доступа: **Автор комментария, модератор или администратор**. | security: - jwt-token.
      Metod: DELETE
        parameters:
          - name: title_id
          - name: review_id
          - name: comment_id

  /users/:
  
    Получить список всех пользователей.
      Права доступа: **Администратор** | security: - jwt-token.
       Metod: GET
        parameters:
          - name: search (Поиск по имени пользователя (username))

    Добавить нового пользователя.
      Права доступа: **Администратор** | security: - jwt-token.
      Поля `email` и `username` должны быть уникальными.
      Metod: POST
        required:
          - username
          - email
        not required:
          - first_name
          - last_name
          - bio
          - role (user", "moderator", "admin". По умолчанию "user".)
        
  /users/{username}/:
  
    Получить пользователя по username.
      Права доступа: **Администратор** | security: - jwt-token.
      Metod: GET
        parameters:
          - name: username

    Изменение данных пользователя по username.
      Права доступа: **Администратор** | security: - jwt-token.
        Metod: PATCH
          parameters:
            - name: username
        required:
          - username
          - email
        not required:
          - first_name
          - last_name
          - bio
          - role (user", "moderator", "admin". По умолчанию "user".)

    Удаление пользователя по username.
      Права доступа: **Администратор** | security: - jwt-token.
        Metod: DELETE
          parameters:
            - name: username

  /users/me/:
  
    Получение данных своей учетной записи.
      Права доступа: **Любой авторизованный пользователь** | security: - jwt-token.
      Metod: GET

    Изменение данных своей учетной записи
      Права доступа: **Любой авторизованный пользователь** | security: - jwt-token.
      Поля `email` и `username` должны быть уникальными.
      Metod: PATCH
        required:
          - username
          - email
        not required:
          - first_name
          - last_name
          - bio  