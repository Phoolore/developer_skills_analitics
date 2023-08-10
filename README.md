# developer_skills_analitics
web site with analitics for back-developer skills value in Russia in rubles
## Технологии
Использовали Flask, bokeh. В процессе сбора и обработки данных pandas.
## Как запустить
1. Клонируем репозиторий, через терминал

```comandline

git clone https://github.com/Phoolore/Flask.git

```

2. Создаем виртуальное окружение, через терминал

```comandline

python -m venv vertualenv

```

3. Активируем виртуальное окружение, через терминал

```comandline

vertualenv\scripts\activate

```

4. Устанавливаем зависимости(фреймворки, пакеты), через терминал

```comandline

pip install -r requirements.txt

```

5. Создаем файл .env и указываем настройки подключения к БД(sqlite и т.п.) и т.п. в нём

```text

DATABASE_URI = sqlite:///db.sqlite3
SECRET_KEY = YOUR_SECRET_KEY

```

6. Запустите flask приложение, через терминал

```comandline

python -m flask run

```
