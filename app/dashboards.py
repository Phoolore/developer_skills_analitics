from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import locale

locale.setlocale(locale.LC_ALL, 'Russian_Russia')


def levelpie(df):#relationship amount for vacancies of different levels
    df1 = df.groupby('level')['level'].count().rename('Counts').reset_index()
    df1 = df1[df1['level'] != missing]
    labels = df1['level']
    values = df1['Counts']
    fig = go.Figure(data = go.Pie(labels = labels, values = values, hoverinfo='label+percent', textinfo='label+percent', textfont_size=15))
    fig.update_layout(width=300, height = 300)
    return fig


def dateline(df):#amount vacancies for each day
    df1 = df.groupby('published_at')['published_at'].count().rename('Counts').reset_index()
    df1 = df1[df1['published_at'] != missing]
    labels = df1['published_at']
    values = df1['Counts']
    fig = go.Figure(data = go.Scatter(x=labels, y=values, mode="lines+text"))
    fig.update_layout(width=500, height = 300)
    return fig


def salbox(df):#salary for different levels, graph which I want to translate
    df1 = df[df['level'] != missing]
    fig = []
    for i in df1['level'].unique():
        df2 = df1.loc[df1['level'] == i]
        df2['salary'] = (df2['min_salary'] + df2['max_salary']) / 2
        fig += [go.Box(y = df2['level'], x = df2['salary'],
                             orientation='h', name=i)]
    #fig.update_layout(width=500, height = 300)
    return fig


df_keys = pd.read_csv("files/key_words.csv", encoding = 'utf8', delimiter = ';')#данные для запросов для таблицы
table = [] #хранитель строк таблицы
target = df_keys.loc[:, :]
missing = 0 #replace for missing values
for i, row in target.iterrows():
    df = pd.read_csv("files/pythonfullvac.csv", encoding = 'utf8', delimiter = ';').fillna(missing) #information for response with filled missing
    avg_sal = int(((df['min_salary'] + df['min_salary'])/2).mean())
    table += [html.Tr([
            html.Th(["Профессия"], scope="col", style={"width":"11%;"}),
            html.Th(["ИТ"], scope="col", style={"width":"11%;"}),
            html.Th([row['name']], scope="col", style={"width":"11%;"}),
            html.Th([row['key']], scope="col", style={"width":"11%;"}),
            html.Th([len(df)], scope="col", style={"width":"11%;"}),
            
            html.Th([dcc.Graph(
            id='dateline' + str(i),
            figure=dateline(df)
            )], scope="col", style={"width":"100%;"}),
            
            html.Th([dcc.Graph(
            id='levelpie'+ str(i),
            figure=levelpie(df)
            )], scope="col", style={"width":"100%;"}),
            
            html.Th([avg_sal], scope="col", style={"width":"11%;"}),
            
            html.Th([dcc.Graph(
            id='salbox'+ str(i),
            figure={'data' : salbox(df),
                    'layout' : {
                        'width' : 500,
                        'height' : 300,
                        'locale': 'Russian_Russia'}} )],#here was a try to change language of graph using framework locale, despite the attributes width and high worked locale not
                    
            scope="col", style={"width":"100%;"}),
        ])
    ]


from . import dash


dash.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Table([
                html.Thead([#names of columns of table 
                    html.Tr([
                        html.Th(["Тип"], scope="col", style={"width":"11%;"}),
                        html.Th(["Сфера"], scope="col", style={"width":"11%;"}),
                        html.Th(["Специализация"], scope="col", style={"width":"11%;"}),
                        html.Th(["Ключевые слова"], scope="col", style={"width":"11%;"}),
                        html.Th(["Кол.вакансий"], scope="col",style={"width":"11%;"}),
                        html.Th(["Даты"], scope="col", style={"width":"11%;"}),
                        html.Th(["Соотношение уровней"], scope="col", style={"width":"11%;"}),
                        html.Th(["Ср.зарплата"], scope="col", style={"width":"11%;"}),
                        html.Th(["Зарплата по уровням"], scope="col", style={"width":"11%;"})
                    ])
                    ],
                    className = "thead-dark"),
                html.Tbody(#table's rows
                    table
                    )
                ], style = {"margin-bottom": 0, "margin-left": 0, "margin-right": "0%", "margin-top": 0}),
          ], width=12)  
    ])

], fluid=True)