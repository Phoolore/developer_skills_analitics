from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.graph_objects as go
import asyncio


app = Flask(__name__)
app.config.from_object('config.Config')
dash = Dash(__name__, server=app, url_base_pathname='/dash/')
db = SQLAlchemy()
db.init_app(app)


from . import models
with app.app_context():
    db.drop_all()
    db.create_all()
from . import GraphQL, views, dashboards


if __name__ == '__main__':
    app.run(debug=True)