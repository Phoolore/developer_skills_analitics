from flask import render_template, redirect, url_for, request
import pandas as pd
import seaborn as sns
import requests

from . import app
from .GraphQL import schema
from .forms import QueryForm

#главная страница с аналитикой
@app.route('/')
def index_page():
    #будущая фича при наведении на навык открывается фрейм на страницу скилл
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


#кастомная страница ошибки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404


#страница подробностей о навыке
@app.route('/skill/<string:name>')
def skill_page(name):
    response = requests.get(f"https://www.google.com/search?q={name}+site:ru.wikipedia.org&hl=ru")
    k = 1
    for i in response.text.split('"'):
        if "https://ru.wikipedia.org/" in i:
            url = i[7:].split("&")[0]
            break
        if i == 'Missing ID':
            k = 0
            break
    if k == 1:
        return render_template('skill.html', url = url, name = name)
    else:
        return page_not_found(f'Страницы навыка "{name}" не найдено, приносим свои извинения, просим написать о данной ошибке на почту agencyUpShot@mail.ru')