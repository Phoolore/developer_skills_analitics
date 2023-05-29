from flask import Flask, render_template, redirect, url_for
import pandas as pd
import seaborn as sns
from . import app, plt
import os


@app.route('/')
def index_page():
    df = pd.read_csv("files/skills_relatives.csv")
    sns.set(style="darkgrid")
    plt.figure(figsize=(10,4), edgecolor = '0', layout='constrained')
    plot = sns.barplot(data=df, x="Название", y="Ценность ₽", color = '0', width = 0.9)
    fig = plot.get_figure()
    fig.savefig("app/static/table.jpg")
    return render_template('index.html', names= df.iloc[:, 0].to_list(), costs = [round(i,2) for i in df.iloc[:, 1].to_list()], length=len(df))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404