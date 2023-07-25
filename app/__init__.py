from dash import Dash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

pd.options.mode.chained_assignment = None #Warnings when work in functions with copy from arguments

# создание главного сервера (app) и страниц с графиками(dash_...)
app = Flask(__name__)
app.config.from_object('config.Config')
dash_table_spec = Dash(
    __name__,
    external_scripts = [
    "static/js/plotly-locale-ru.js"
    ],
    server=app,
    url_base_pathname='/table_spec/',
    update_title='Загрузка...',
    assets_folder = 'static'
    )
dash_table_skill = Dash(
    __name__,
    external_scripts = [
    "static/js/plotly-locale-ru.js"
    ],
    server=app,
    url_base_pathname='/table_skill/',
    update_title='Загрузка...',
    assets_folder = 'static'
    )
superpage = Dash(
    __name__, 
    external_scripts = [
                        "static/js/plotly-locale-ru.js"
                       ],
    server=app,
    url_base_pathname='/',
    update_title='Загрузка...',
    assets_folder = 'static'
    )

# загрузка favicon для сайтов графиков(внутрение сайты)
dash_table_spec._favicon = "files/internal_pages_logo.ico"
dash_table_skill._favicon = "files/internal_pages_logo.ico"

# подключение бд
db = SQLAlchemy()
db.init_app(app)


from . import app, dashboard, models

with app.app_context():
    # db.drop_all()
    db.create_all()
from . import GraphQL, views, newdash

if __name__ == '__main__':
    app.run()