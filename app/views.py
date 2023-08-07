from flask import render_template, redirect, url_for, request
import pandas as pd

from . import app
from .GraphQL import schema
from .forms import QueryForm
from .graph import DateLine, LevelPie,  missing


#кастомная страница ошибки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404


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


@app.route("/", methods=['GET', 'POST'])
def index_page():
    """Построение графиков и упаковка в html"""
    mode = ["Специализации","Навыки"][0]
    rows = [] #хранитель строк будущего df с вакансиями
    with app.app_context():
        query = '{getSpecializations{ edges { node {name, vacancies {edges { node {name, minSalary, maxSalary, experience, keySkills, publishedAt, status, city} } } } } } }' #Запрос к GraphQL для получения специализаций и прокрепленных к ним ваканиям
        data = schema.execute(query).data

    result = data['getSpecializations']['edges'] #открытие и переход к массиву с специализациями
    if result != None:
        #передача данных из ответа от GraphQL в df
        for spec in result: #перебор специализаций
            for vac in spec['node']['vacancies']['edges']:#перебор вакансий
                rows += [{
                    'specialization' : spec['node']['name'],
                    'job_title' : vac['node']['name'],
                    'min_salary' : vac['node']['minSalary'], 
                    'max_salary' : vac['node']['maxSalary'],
                    'experience' : vac['node']['experience'].replace('between', 'От ').replace('And', ' до '),
                    'key_skills' : vac['node']['keySkills'].replace("'", ""),
                    'published_at' : vac['node']['publishedAt'], 
                    'status' : vac['node']['status'],
                    'city' : vac['node']['city']
                    }]

    df_full = pd.DataFrame(rows, index = [i for i in range(len(rows))]).fillna(missing)#полный df для специализаций и скиллов
    cities_list = df_full['city'].unique().tolist().remove(missing)
    filter_list = [] #хранитель вариантов для фильтров

    return render_template("index.html", 
                           GeneralDateLine = DateLine(df_full),
                           GeneralLevelPie = LevelPie(df_full)
                           )