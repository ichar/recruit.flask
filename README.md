# Recruit

Призывник-ВС

### Создание виртуального окружения

- Установить Abaconda:

- Создать каталог проекта:

    mkdir ~/{project_name}

- Перейти в каталог проекта:

    cd ~/{project_name}

- Выполнить команду:

    conda create --prefix ./venv python=3.7.3

- Активировать виртуальное окружение:

    conda activate ./venv

- Установить необходимые пакеты:

    pip install -r requirements.txt
    pip install -r requirements-dev.txt

- В каталоге ~/{project_name} создать файл .env со строкой подключения к БД:

    DEVELOPMENT_DATABASE_URL="postgresql://recruit:recruit@localhost/recruit"

    где: {имя_сервера_бд}://{пользователь_бд}:{пароль}@{хост}/{имя_бд}

- Создание базы данных:

    flask database create

- Обновление базы данных:

    flask database update
    flask database update_fias

- Для работы с pdf (html->pdf) установить:

  $ sudo apt-get install wkhtmltopdf


