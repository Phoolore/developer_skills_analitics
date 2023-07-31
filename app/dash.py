from dash import html, dcc, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from . import app, superpage
from .GraphQL import schema

size = 10 #размер текста на графиках
missing = 0 #замена для пустых клеток
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']


def avg_sal(df, df_bool = False):
    if df_bool == True: #Режим возврата массива
        return (df['min_salary'] + df['max_salary'])/2
    avg = int(((df['min_salary'] + df['max_salary'])/2).mean())
    return avg


def counts_table(name, df_full, avg_sal_bool = False):
    counts_table = []
    df = df_full.loc[df_full[name] != missing]
    for i, row in df.groupby(name)[name].count().rename("counts").reset_index().iterrows():
        result = [
            html.Th(row[name]),
            html.Th( row['counts'])
        ] 
        if avg_sal_bool == True:
            result += [html.Th(avg_sal(df.loc[df[name] == row[name]]))]
        counts_table += [html.Tr(result)]
    return counts_table


def get_html(path):
    with open("app/templates/" + path + ".html", "r", encoding = "utf8") as f:
        return html.Div(html.Iframe(id='side nav', style={'border-width': '5', 'width': '100%', 'height': '100%', 'border': 'none', 'overflow': 'auto'},srcDoc = f.read()))


def to_html(graph):
    return html.Div(html.Iframe(id='side nav', style={'border-width': '5', 'width': '100%', 'height': '100%', 'border': 'none', 'overflow': 'auto'},srcDoc = graph))


def layout():
    layout = dbc.Container([
        get_html("navigation"),
        dbc.Row([
            dbc.Col( width = 10),
            dbc.Col(get_html("side_navigation"), width = 2),
        ]),
        get_html("footer")
    ], style = { "background-image": 'url("static/files/background.png")'})
    return layout


superpage.layout = layout()