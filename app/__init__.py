from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.graph_objects as go
import asyncio


app = Flask(__name__)
app.config.from_object('config.Config')
dash_table_spec = Dash(__name__, server=app, url_base_pathname='/table_spec/', update_title='Загрузка...', assets_folder = 'app/static')
dash_table_skill = Dash(__name__, server=app, url_base_pathname='/table_skill/', update_title='Загрузка...', assets_folder = 'app/static')
db = SQLAlchemy()
db.init_app(app)


from . import models
with app.app_context():
    db.drop_all()
    db.create_all()
from . import GraphQL, views, dash


if __name__ == '__main__':
    app.run(debug=True)