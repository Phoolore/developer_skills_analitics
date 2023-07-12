from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.graph_objects as go
import asyncio

# создание главного сервера (app) и страниц с графиками(dash_...)
app = Flask(__name__)
app.config.from_object('config.Config')
dash_table_spec = Dash(__name__, server=app, url_base_pathname='/table_spec/', update_title='Загрузка...', assets_folder = 'static')
dash_table_skill = Dash(__name__, server=app, url_base_pathname='/table_skill/', update_title='Загрузка...', assets_folder = 'static')

# загрузка favicon для сайтов графиков(внутрение сайты)
dash_table_spec._favicon = "files/internal_pages_logo.ico"
dash_table_skill._favicon = "files/internal_pages_logo.ico"

# подключение бд
db = SQLAlchemy()
db.init_app(app)


from . import models
with app.app_context():
    db.drop_all()
    db.create_all()
from . import GraphQL, views, dash


if __name__ == '__main__':
    app.run(debug=True)