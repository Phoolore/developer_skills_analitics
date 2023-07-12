from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json

from . import app
from .GraphQL import schema

size = 10 #размер текста на графиках


def levelpie(df):#соотношение колличества вакансий по уровням
     #подготовка данных
    df1 = df.groupby('experience')['experience'].count().rename('Counts').reset_index()
    df1 = df1[df1['experience'] != missing]
    
     #создание графика
    labels = df1['experience']
    values = df1['Counts']
    fig = go.Figure(
        data = go.Pie(
            labels = labels, 
            values = values, 
            hoverinfo='label+percent', 
            textinfo='label+percent', 
            textfont_size = size
            )
                    )
    
    #настройка отображения графика
    fig.update_layout(
        width=300, 
        height = 300,
        font = dict(
            size = size
            )
        )
    return fig


def dateline(df):#график колличества вакансий по датам загрузки
    #подготовка данных
    df1 = df.groupby('published_at')['published_at'].count().rename('Counts').reset_index()
    df1 = df1[df1['published_at'] != missing]
    
    #создание графика
    labels = df1['published_at']
    values = df1['Counts']
    fig = go.Figure(data = go.Scatter(x=labels, y=values, mode="lines+text"))
    
    #настройка отображения графика
    fig.update_layout(
        width=500, 
        height = 300,
        font = dict(
            size = size
            )
        )
    return fig


def salbox(df):#зп по уровням
    # подготовка данных
    df.loc[:, 'salary'] = (df['min_salary'] + df['max_salary']) / 2
    df_full = df[df['experience'] != missing]
    
    # создание специальной фигуры с отсеками для графиков
    specs = [[{"type" : "box"}]] * len(df_full['experience'].unique())
    fig = make_subplots(
        print_grid = False, 
        rows = len(df_full['experience'].unique()), 
        cols = 1, 
        shared_xaxes=True, 
        shared_yaxes=False, 
        specs = specs, 
        vertical_spacing = 0)
    
    # перебор каждой группы уровней для создания и настройки её графика
    for i, experience in enumerate(df_full['experience'].unique()):
        df_l = df_full.loc[df_full['experience'] ==  experience]
        
        #preparation for figure in subplots
        fig_prep = go.Box(
            y = df_l['experience'], 
            x = df_l['salary'],
            orientation='h',
            name= experience
            ) 
        
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
        fig.update_yaxes(
            showgrid = True
        )
        
        #перевод точек путем добавление их русских копий и визуальные фиксы, так как текст точек отображается на оси
        fig.update_xaxes(
            showgrid = True,
            showticklabels = False,
            minor = {
                'gridcolor': '#fff',
                'dtick' : 100000
            },
            ticktext=[
                'Минимум:' + str(round(minimum/1000)) + "k",
                'Нижняя граница:' + str(round(lower_fence/1000)) + "k",
                'Q1:' + str(round(q1/1000)) + "k",
                'Медиана:' + str(round(median/1000)) + "k",
                'Q3:' + str(round(q3/1000)) + "k",
                'Верхняя граница:' + str(round(upper_fence/1000)) + "k",
                'Максимум:' + str(round(maximum/1000)) + "k"
                ],
            tickvals=[
                minimum, 
                lower_fence, 
                q1,
                median, 
                q3, 
                upper_fence,  
                maximum
                ], 
            row=i+1, 
            col=1)
        
    #настройка отображения графика
    fig.update_layout(
        width=500,
        height = 300,
        font = dict(
            size = size
        )
        )
    return fig

with app.app_context():
    query = '{getSpecializations{ edges { node {name, vacancies {edges { node {name, minSalary, maxSalary, experience, publishedAt} } } } } } }' #Запрос к GraphQL для получения специализаций и прокрепленных к ним ваканиям
    result = schema.execute(query).data
with open("data.txt", "w+") as f:
    f.write(str(result))
result = result['getSpecializations']['edges'] #открытие и переход к массиву с специализациями

#передача данных из GraphQL в df
missing = 0 #замена для пустых клеток
rows = [] #хранитель строк будущего df с вакансиями
for spec in result: #перебор специализаций
    for vac in spec['node']['vacancies']['edges']:#перебор вакансий
        rows += [{
            'specialization' : spec['node']['name'],
            'job_title' : vac['node']['name'],
            'min_salary' : vac['node']['minSalary'], 
            'max_salary' : vac['node']['maxSalary'],
            'experience' : vac['node']['experience'].replace('between', 'От ').replace('And', ' до '),
            'published_at' : vac['node']['publishedAt']
            }]
df_full = pd.DataFrame(rows, index = [i for i in range(len(rows))]).fillna(missing)#полный df для специализаций и скиллов

df_spec = df_full.loc[:, :] #Заготовка для будущих фильтров специализаций

table_spec = [] #хранитель строк таблицы специализаций
table_skill = [] #хранитель строк таблицы навыков


for i, spec in enumerate(df_spec['specialization'].unique()):#перебор специализаций
    df = df_spec[df_spec['specialization'] == spec]
    avg_sal = int(((df['min_salary'] + df['min_salary'])/2).mean())
    table_spec += [html.Tr([
            html.Th(["Специализация"], scope="col"),
            html.Th(["ИТ"], scope="col"),
            html.Th([spec], scope="col"),
            html.Th([len(df)], scope="col"),
            
            html.Th([dcc.Graph(
            id='dateline' + str(i + 1),
            figure=dateline(df),
            animate = False
            )], scope="col"),
            
            html.Th([dcc.Graph(
            id='levelpie'+ str(i + 1),
            figure=levelpie(df),
            animate = False
            )], scope="col"),
            
            html.Th([avg_sal], scope="col"),
            
            html.Th([dcc.Graph(
            id='salbox'+ str(i),
            figure = salbox(df),
            animate = False
            )], scope="col"),
        ])
    ]



from . import dash_table_spec


dash_table_spec.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            [
                html.Table(
                    [
                        html.Thead(
                            [
                                #names of columns of table 
                                html.Tr([
                                    html.Th(["Тип"], scope="col"),
                                    html.Th(["Сфера"], scope="col"),
                                    html.Th(["Специализация"], scope="col"),
                                    html.Th(["Кол.вакансий"], scope="col"),
                                    html.Th(["Даты"], scope="col"),
                                    html.Th(["Соотношение уровней"], scope="col"),
                                    html.Th(["Ср.зарплата"], scope="col"),
                                    html.Th(["Зарплата по уровням"], scope="col")
                                    ]
                                )
                            ],
                            className = "thead-dark"
                            ),
                        html.Tbody(#строки таблицы
                            table_spec
                        )
                    ], 
                    style = {
                        "margin-bottom": 0,
                        "margin-left": 0,
                        "margin-right": "0%",
                        "margin-top": 0
                        }
                    ),
        ], 
        width=12
        )
    ])

], fluid=True)


from . import dash_table_skill

dash_table_skill.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            [
                html.Table(
                    [
                        html.Thead(#names of columns of table 
                            [
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
                        ], 
                    style = {
                        "margin-bottom": 0, 
                        "margin-left": 0, 
                        "margin-right": "0%", 
                        "margin-top": 0
                        }
                    ),
                ], 
            width=12)
    ])

], fluid=True)