from flask import render_template, redirect, url_for, request
import pandas as pd
import requests

from . import app
from .GraphQL import schema
from .forms import QueryForm
from .dashboard import dashboards
from config import GOOGLE_API_KEY , GOOGLE_ENGINE_ID

#кастомная страница ошибки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404


#главная страница с аналитикой
@app.route('/old/')
def index_page():
    #будущая фича при наведении на навык открывается фрейм на страницу скилл
    dashboards()
    return render_template('index.html')


#страница запросов GraphQL
@app.route('/graphql/', methods=['GET', 'POST'])
def graphql_query_page():
    query = '{getSpecializations{ edges { node {name, vacancies {edges { node {name, minSalary, maxSalary, experience, publishedAt} } } } } } }' #Запрос к GraphQL для получения специализаций и прокрепленных к ним ваканиям
    result = schema.execute(query)
    with open("data.txt", "w+") as f:
        f.write(str(result))
    if request.method == 'POST':
        query = request.form['query']
    else:
        query = ''
    form = QueryForm()
    result = schema.execute(query)
    data = result.data
    errors = result.errors
    return render_template('graphql.html', data = data, query = query, errors = errors, form = form)


#страница подробностей о навыке
@app.route('/description/<string:name>')
def description_page(name):
    url = f'https://ru.wikipedia.org/w/index.php?search={name}'#ссылка на ресурс
    if "Результаты поиска" not in requests.get(url).content: #Проверка что сайт найден
        return render_template('description.html', url = url, name = name)
    else:
        return page_not_found(f'Страницы навыка "{name}" не найдено, приносим свои извинения, просим написать о данной ошибке на почту agencyUpShot@mail.ru')