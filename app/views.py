from flask import Flask, render_template, redirect, url_for
import pandas as pd
import seaborn as sns
from . import app
import os
# from flask_graphql import GraphQLView
# from .GraphQL import schema


# app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
#     'graphql',
#     schema = schema,
#     graphiql = True
# ))

@app.route('/')
def index_page():
    df = pd.read_csv("files/all_data.csv").sort_values(by='salary', ascending=False)
    sns.set(style="darkgrid")
    plot = sns.barplot(data=df.iloc[:10, :], x="skills", y="salary", color = '0', width = 0.9)
    fig = plot.get_figure()
    fig.savefig("app/static/table.jpg")
    df = pd.read_csv("files/all_data.csv").sort_values(by='salary', ascending=False)
    return render_template('index.html', names= df.iloc[:, 0].to_list(), popularity = [round(i,2) for i in df.iloc[:, 1].to_list()], salary = [round(i,2) for i in df.iloc[:, 4].to_list()], length=len(df))


@app.route('/testtest/')
def test_page():
    return render_template('test.html', fig = fig)


@app.route('/shamil/<path:a>')
def files(a):
    print("app/files/" + a, os.getcwd())
    try:
        print("templates/" + a)
        return render_template(a)
    except Exception as e:
        page_not_found(e)
    

@app.route('/skill/<string:name>')
def skill_page(name):
    df = pd.read_csv("files/skill.csv", delimiter=';')
    skill = df.loc[df.name == name].squeeze(axis = 0)
    length = len(skill) - 3
    return render_template('skill.html', skill = skill, length = length)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404
