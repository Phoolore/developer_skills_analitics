# developer_skills_analitics
web site with analitics for back-developer skills value in Russia in rubles
## Технологии
Использовали Flask, seaborn. В процессе сбора и обработки данных pandas.

## Как запустить
1. Клонируем репозиторий
'''comandline

git clone https://github.com/Phoolore/Flask.git

'''
2. Создаем виртуальное окружение
'''comandline

python -m venv vertualenv

'''
3. Устанавливаем зависимости(фреймворки, пакеты)
'''comandline

pip install -r requirements.txt

'''
4. Создаем файл .env и укажите настройки подключения к БД(sqlite и т.п.) и т.п.

'''.env

SECRET_KEY = YOUR_SECRET_KEY

'''

5. Запустите flask приложение
'''comandline

python -m flask run

'''