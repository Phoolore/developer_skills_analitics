# developer_skills_analitics
web site with analitics for back-developer skills value in Russia in rubles
## Технологии
Использовали Flask, seaborn, dash, plotly. В процессе сбора и обработки данных pandas.


## Сайт с аналитикой
![Главная страница](developer_skills_analitics\app\static\files\index.jpg "Главная страница")

<hr></hr>

![Страница навыка](developer_skills_analitics\app\static\files\Skill.jpg "Страница навыка")
## Как запустить
1. Клонируем репозиторий

'''comandline

git clone https://github.com/Phoolore/Flask.git

'''

2. Создаем виртуальное окружение

'''comandline

python -m venv vertualenv

'''

3. Создаем виртуальное окружение

'''comandline

vertualenv\scripts\activate

'''

4. Устанавливаем зависимости(фреймворки, пакеты)

'''comandline

pip install -r requirements.txt

'''

5. Создаем файл .env и укажите настройки подключения к БД(sqlite и т.п.) и т.п.

'''.env

DATABASE_URI = sqlite:///db.sqlite3

SECRET_KEY = YOUR_SECRET_KEY

'''

6. Запустите flask приложение

'''comandline

python -m flask run

'''
