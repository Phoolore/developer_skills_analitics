from datetime import datetime, date, time
from flask import Flask, render_template, redirect, url_for
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from . import app
import os


@app.route('/')
def index_page():
    year = datetime.now().year
    data = pd.read_csv("files/skills_relatives.csv")
    costs = [str(round(i, 2) * 100) for i in data.iloc[0, :].to_list()]
    sns.set(style="darkgrid")
    fig = sns.displot(data.iloc[0, :], x=data.columns )
    fig.savefig("app/static/table.jpg")
    return render_template('index.html', columns=data.columns, data=costs, length=len(costs), image = fig)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404