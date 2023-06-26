from flask import render_template, redirect, url_for, request
import pandas as pd
import seaborn as sns
from . import app
from .GraphQL import schema
from .forms import QueryForm

#главная страница с аналитикой
@app.route('/')
def index_page():
    #будущая фича при наведении на навык открывается фрейм на страницу скилл
    df = pd.read_csv("files/all_data.csv").sort_values(by='salary', ascending=False)
    sns.set(style="darkgrid")
    plot = sns.barplot(data=df.iloc[:10, :], x="skills", y="salary", color = '0', width = 0.9)
    fig = plot.get_figure()
    fig.savefig("app/static/table.jpg")
    df = pd.read_csv("files/all_data.csv").sort_values(by='salary', ascending=False)
    return render_template('index.html', names= df.iloc[:, 0].to_list(), popularity = [round(i,2) for i in df.iloc[:, 1].to_list()], salary = [round(i,2) for i in df.iloc[:, 4].to_list()], length=len(df))


#страница подробностей о навыке
@app.route('/skill/<string:name>')
def skill_page(name):
    df = pd.read_csv("files/skill.csv", delimiter=';')
    skill = df.loc[df.name == name].squeeze(axis = 0)
    length = len(skill) - 3
    return render_template('skill.html', skill = skill, length = length)

#страница запросов GraphQL
@app.route('/graphql/', methods=['GET', 'POST'])
def graphql_query_page():
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