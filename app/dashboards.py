from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
#from .fullvacparser import parser #for future update


def levelpie(df):#соотношение колличества вакансий по уровням
    df1 = df.groupby('level')['level'].count().rename('Counts').reset_index()
    df1 = df1[df1['level'] != missing]
    labels = df1['level']
    values = df1['Counts']
    fig = go.Figure(data = go.Pie(labels = labels, values = values, hoverinfo='label+percent', textinfo='label+percent', textfont_size=15))
    fig.update_layout(width=300, height = 300)
    return fig


def dateline(df):#график колличества вакансий по датам загрузки
    df1 = df.groupby('published_at')['published_at'].count().rename('Counts').reset_index()
    df1 = df1[df1['published_at'] != missing]
    labels = df1['published_at']
    values = df1['Counts']
    fig = go.Figure(data = go.Scatter(x=labels, y=values, mode="lines+text"))
    fig.update_layout(width=500, height = 300)
    return fig


def salbox(df):#зп по уровням
    df_full = df[df['level'] != missing]
    specs = [[{"type" : "box"}]] * len(df_full['level'].unique())
    fig = make_subplots(
        print_grid = True, 
        rows = len(df_full['level'].unique()), 
        cols = 1, shared_xaxes=True, 
        shared_yaxes=True, 
        specs = specs, 
        vertical_spacing = 0)
    for i, level in enumerate(df_full['level'].unique()):
        df_l = df_full.loc[df_full['level'] ==  level]
        df_l['salary'] = (df_l['min_salary'] + df_l['max_salary']) / 2
        
        fig_prep = go.Box(
            y = df_l['level'], 
            x = df_l['salary'],
            orientation='h', name= level) #preparation for figure in subplots
        
        fig.add_trace(fig_prep, row=i+1, col=1)
        
        # Вычисляем значения q1, q3, iqr и медианы
        q1 = np.percentile(df_l['salary'], 25)
        q3 = np.percentile(df_l['salary'], 75)
        iqr = q3 - q1
        median = np.median(df_l['salary'])
        
        # Вычисляем минимум и максимум
        maximum = df_l['salary'].max()
        minimum = df_l['salary'].min()
        
        #Вычисляем границы(усы)
        lower_fence = q1 - iqr * 1.5
        upper_fence = q3 + iqr * 1.5
        fig.update_xaxes(
            showticklabels=False,
            ticktext=['Минимум:' + str(round(minimum/1000)) + "k", 'Нижняя граница:' + str(round(lower_fence/1000)) + "k", 'Q1:' + str(round(q1/1000)) + "k", 'Медиана:' + str(round(median/1000)) + "k", 'Q3:' + str(round(q3/1000)) + "k", 'Верхняя граница:' + str(round(upper_fence/1000)) + "k", 'Максимум:' + str(round(maximum/1000)) + "k"],
            tickvals=[minimum, 
                lower_fence, 
                q1,
                median, 
                q3, 
                upper_fence,  
                maximum
                ], 
            row=i+1, 
            col=1)
        
    fig.update_layout(
        legend = dict(
            traceorder="reversed"
        ),
        width=500,
        height = 300)
    return fig


df_keys = pd.read_csv("files/key_words.csv", encoding = 'utf8', delimiter = ';')#данные для запросов для таблицы
table_spec = [] #хранитель строк таблицы специализаций
table_skill = [] #хранитель строк таблицы навыков
target = df_keys.loc[:, :] #Заготовка для будущих фильтров
missing = 0 #замена для пустых клеток
for i, row in target.iterrows():
    df = pd.read_csv("files/pythonfullvac.csv", encoding = 'utf8', delimiter = ';').fillna(missing) #данные из запроса для аналитики, с заполнеными потерянными данными
    avg_sal = int(((df['min_salary'] + df['min_salary'])/2).mean())
    table_spec += [html.Tr([
            html.Th(["Профессия"], scope="col", style={"width":"5%;"}),
            html.Th(["ИТ"], scope="col", style={"width":"5%;"}),
            html.Th([row['name']], scope="col", style={"width":"5%;"}),
            html.Th([row['key']], scope="col", style={"width":"5%;"}),
            html.Th([len(df)], scope="col", style={"width":"5%;"}),
            
            html.Th([dcc.Graph(
            id='dateline' + str(i + 1),
            figure=dateline(df),
            animate = False
            )], scope="col", style={"width":"100%;"}),
            
            html.Th([dcc.Graph(
            id='levelpie'+ str(i + 1),
            figure=levelpie(df),
            animate = False
            )], scope="col", style={"width":"100%;"}),
            
            html.Th([avg_sal], scope="col", style={"width":"5%;"}),
            
            html.Th([dcc.Graph(
            id='salbox'+ str(i),
            figure = salbox(df),
            animate = False
            )], scope="col", style={"width":"100%;"}),
        ])
    ]



from . import dash


dash.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Table([
                html.Thead([#names of columns of table 
                    html.Tr([
                        html.Th(["Тип"], scope="col", style={"width":"5%;"}),
                        html.Th(["Сфера"], scope="col", style={"width":"5%;"}),
                        html.Th(["Специализация"], scope="col", style={"width":"5%;"}),
                        html.Th(["Ключевые слова"], scope="col", style={"width":"5%;"}),
                        html.Th(["Кол.вакансий"], scope="col",style={"width":"5%;"}),
                        html.Th(["Даты"], scope="col", style={"width":"33%;"}),
                        html.Th(["Соотношение уровней"], scope="col", style={"width":"33%;"}),
                        html.Th(["Ср.зарплата"], scope="col", style={"width":"5%;"}),
                        html.Th(["Зарплата по уровням"], scope="col", style={"width":"34%;"})
                    ])
                    ],
                    className = "thead-dark"),
                html.Tbody(#строки таблицы
                    table_spec
                    )
                ], style = {"margin-bottom": 0, "margin-left": 0, "margin-right": "0%", "margin-top": 0}),
          ], width=12),
        dbc.Col([
            html.Table([
                html.Thead([#names of columns of table 
                    html.Tr([
                        html.Th(["Тип"], scope="col", style={"width":"11%;"}),
                        html.Th(["Сфера"], scope="col", style={"width":"11%;"}),
                        html.Th(["Навык"], scope="col", style={"width":"11%;"}),
                        html.Th(["Кол.вакансий"], scope="col",style={"width":"11%;"}),
                        html.Th(["Даты"], scope="col", style={"width":"11%;"}),
                        html.Th(["Соотношение уровней"], scope="col", style={"width":"11%;"}),
                        html.Th(["Ср.зарплата"], scope="col", style={"width":"11%;"}),
                        html.Th(["Зарплата по уровням"], scope="col", style={"width":"11%;"})
                    ])
                    ],
                    className = "thead-dark"),
                html.Tbody(#строки таблицы
                    table_skill
                    )
                ], style = {"margin-bottom": 0, "margin-left": 0, "margin-right": "0%", "margin-top": 0}),
          ], width=12)
    ])

], fluid=True)