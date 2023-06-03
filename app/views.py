from flask import Flask, render_template, redirect, url_for
import pandas as pd
import seaborn as sns
from . import app, plt
import os


@app.route('/')
def index_page():
    df = pd.read_csv("files/skills_relatives.csv").sort_values(by='Ценность ₽', ascending=True)
    sns.set(style="darkgrid")
    plt.figure(figsize=(9.5,4), edgecolor = '0', layout='constrained')
    plot = sns.barplot(data=df, x="Название", y="Ценность ₽", color = '0', width = 0.9)
    fig = plot.get_figure()
    fig.savefig("app/static/table.jpg")
    df = pd.read_csv("files/skills_relatives.csv").sort_values(by='Ценность ₽', ascending=False)
    return render_template('index.html', names= df.iloc[:, 0].to_list(), costs = [round(i,2) for i in df.iloc[:, 1].to_list()], length=len(df))


@app.route('/skill/<string:name>')
def skill_page(name):
    df = pd.read_csv("files/skill.csv", delimiter=';')
    skill = df.loc[df.name == name].squeeze(axis = 0)
    length = len(skill) - 3
    return render_template('skill.html', skill = skill, length = length)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404