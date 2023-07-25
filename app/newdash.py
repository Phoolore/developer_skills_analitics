from flask import url_for
from dash import html

from . import app, superpage


def navbar():
    with app.app_context():
        layout = html.Div([
            html.A("Главная", href = '/old/')
            ], className = "navbar")
    return layout


superpage.layout = navbar()
