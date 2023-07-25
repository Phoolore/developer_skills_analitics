from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .GraphQL import schema
from . import app, dash_table_spec, dash_table_skill

size = 10 #размер текста на графиках
missing = 0 #замена для пустых клеток
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
dash_table_spec.layout = html.H1("None") #Временная заставка, иначе None, и ошибка,что None быть не может
dash_table_skill.layout = html.H1("None") #Временная заставка, иначе None, и ошибка,что None быть не может


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
            textinfo='percent', 
            textfont_size = size,
            hole=0.6, 
            marker=dict(line=dict(color='black', width=5))
            )
                    )
    
    # Настройка цветов
    fig.update_traces(marker=dict(colors=colors))
    
    #настройка отображения графика
    fig.update_layout(
        width=300, 
        height = 300,
        font = dict(
            size = size
            )
        )
    return fig


def dateline(df, name):#график колличества вакансий по датам загрузки
    #подготовка данных
    df1 = df.groupby('published_at')['published_at'].count().rename('Counts').reset_index()
    df1 = df1[df1['published_at'] != missing]
    
    #создание графика
    color = 'rgb(250, 200, 50)'
    labels = df1['published_at']
    values = df1['Counts']
    fig = go.Figure(
        data = go.Scatter(
            x=labels, 
            y=values, 
            mode="lines+text+markers",
            line=dict(color=color, width=6),
            marker=dict(
                color='rgb(0, 0, 0)', 
                size=15, 
                line=dict(width=5, color=color)
                ),
            hovertemplate = "%{x};Кол.вакансий:%{y} ",
            name = name
            )
        )
    
    # настройка языка и добавление слайдера выбора дат
    fig.update_xaxes(
        rangeslider =  {'visible': True, 'bgcolor' : 'rgba(0, 0, 0, 0)', 'bordercolor' : 'rgba(0, 0, 0, 256)', 'borderwidth' : 1} #создание слайдера
    )
    
    #настройка отображения графика
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        xaxis={'gridcolor': 'rgba(0, 0, 0, 256)'},  # Изменение цвета разметки на черный
        yaxis={'title': 'Кол.вакансий', 'gridcolor': 'rgba(0, 0, 0, 256)'},  # Изменение цвета разметки на черный
        width=500, 
        height = 300,
        margin = dict(
            b = 0,
            l = 0,
            r = 0,
            t = 0
            ),
        autosize=True,
        font = dict(
            color='rgb(0, 0, 0)',
            size = size
            )
        )
    return fig


def salbox(df):#зп по уровням
    # подготовка данных
    df['salary'] = (df['min_salary'] + df['max_salary']) / 2
    df_full = df.loc[df['experience'] != missing]
    
    # создание специальной фигуры с отсеками для графиков
    fig = go.Figure()
    
    # перебор каждой группы уровней для создания и настройки её графика
    for i, level in enumerate(df_full['experience'].unique()):
        df_level = df_full.loc[df_full['experience'] == level]
        fig.add_trace(
            go.Box(
                hoverlabel = dict(
                    font = dict(
                        size = size
                    )
                ),
                y = df_level['experience'], 
                x = df_level['salary'],
                orientation='h',
                marker=dict(color=colors[i]),
                name=level
                )
            )
        
    #настройка отображения графика
    fig.update_layout(
        plot_bgcolor='rgba(255, 255, 255, 0)',  # Цвет фона
        paper_bgcolor='rgba(255, 255, 255, 0)',  # Цвет фона графика
        xaxis=dict(
            showgrid=True,# Включение сетки по оси X
            gridcolor='black',# Цвет сетки
            zeroline=False  # Отключение линии в нуле по оси X
        ),
        yaxis=dict(
            showgrid=False,  # Включение сетки по оси Y
            gridcolor='black',  # Цвет сетки
            zeroline=False  # Отключение линии в нуле по оси Y
        ),
        legend=dict(
            bgcolor='rgba(255, 255, 255,  0)'
            ),
        width=500,
        height = 300,
        font = dict(
            size = size
        )
        )
    return fig


# ссоздание таблиц по запросу
def dashboards(spec = None, skill = None):
    rows = [] #хранитель строк будущего df с вакансиями
    with app.app_context():
        query = '{getSpecializations{ edges { node {name, vacancies {edges { node {name, minSalary, maxSalary, experience, keySkills, publishedAt, status} } } } } } }' #Запрос к GraphQL для получения специализаций и прокрепленных к ним ваканиям
        data = schema.execute(query).data
    
    result = data['getSpecializations']['edges'] #открытие и переход к массиву с специализациями

    if result != None:
        #передача данных из ответа от GraphQL в df
        for spec in result: #перебор специализаций
            for vac in spec['node']['vacancies']['edges']:#перебор вакансий
                rows += [{
                    'specialization' : spec['node']['name'],
                    'job_title' : vac['node']['name'],
                    'min_salary' : vac['node']['minSalary'], 
                    'max_salary' : vac['node']['maxSalary'],
                    'experience' : vac['node']['experience'].replace('between', 'От ').replace('And', ' до '),
                    'key_skills' : vac['node']['keySkills'].replace("'", ""),
                    'published_at' : vac['node']['publishedAt'], 
                    'status' : vac['node']['status']
                    }]

    df_full = pd.DataFrame(rows, index = [i for i in range(len(rows))]).fillna(missing)#полный df для специализаций и скиллов

    df_spec = df_full.loc[df_full['status']] #Заготовка для будущих фильтров специализаций
    df_skill = df_full.loc[df_full['status']] #Заготовка для будущих фильтров специализаций

    table_spec = [] #хранитель строк таблицы специализаций
    table_skill = [] #хранитель строк таблицы навыков

    if len(df_full) > 0:
        for i, spec in enumerate(df_spec['specialization'].unique()):#перебор специализаций
            df = df_spec[df_spec['specialization'] == spec] #выборка по специализации
            avg_sal = int(((df['min_salary'] + df['min_salary'])/2).mean())
            table_spec += [
                html.Tr([
                    html.Td(["Специализация"]),
                    html.Td(["ИТ"]),
                    html.Td([spec]),
                    html.Td([len(df)]),
                    
                    html.Td([dcc.Graph(
                    id='dateline' + str(i + 1),
                    config={"locale": 'ru'},
                    figure=dateline(df, spec),
                    )]),
                    
                    html.Td([dcc.Graph(
                    id='levelpie'+ str(i + 1),
                    config={"locale": 'ru'},
                    figure=levelpie(df),
                    )]),
                    
                    html.Td([avg_sal]),
                    
                    html.Td([dcc.Graph(
                    id='salbox'+ str(i),
                    config={"locale": 'ru'},
                    figure = salbox(df),

                    )])
                ])
            ]

        for skills_packs in df_skill['key_skills'].unique(): #получение наборов навыков из вакансий без повторений
            for i, skill in enumerate(skills_packs.replace("[", "").replace("]", "").split(','))  :#перебор навыков
                df = df_skill[df_skill['key_skills'].str.contains(skill)] #выборка вакансий с навыком
                
                avg_sal = int(((df['min_salary'] + df['min_salary'])/2).mean()) #средняя зарплата
                
                table_skill += [
                    html.Tr([
                        html.Td(["Навык"]),
                        html.Td(["ИТ"]),
                        html.Td([skill]),
                        html.Td([len(df)]),
                        html.Td([dcc.Graph(
                            id='dateline' + str(i + 1),
                            config={"locale": 'ru'},
                            figure=dateline(df, skill)
                            )]),
                            
                            html.Td([dcc.Graph(
                            id='levelpie'+ str(i + 1),
                            config={"locale": 'ru'},
                            figure=levelpie(df)
                            )]),
                            
                            html.Td([avg_sal]),
                            
                            html.Td([dcc.Graph(
                            id='salbox'+ str(i),
                            config={"locale": 'ru'},
                            figure = salbox(df)
                            )])
                    ])
                ]

    # localization
    dash_table_spec.scripts.append_script({"external_url": "https://cdn.plot.ly/plotly-locale-ru-latest.js"})

    dash_table_spec.layout = html.Table(
        [
            html.Thead(
                [
                    #names of columns of table 
                    html.Tr([
                        html.Th(["Тип"]),
                        html.Th(["Сфера"]),
                        html.Th(["Специализация"]),
                        html.Th(["Кол.вакансий"]),
                        html.Th(["Даты"]),
                        html.Th(["Соотношение уровней"]),
                        html.Th(["Ср.зарплата"]),
                        html.Th(["Зарплата по опыту работы"])
                        ])
                    ],
                className = "thead-dark"
                ),
            html.Tbody(#строки таблицы
                       table_spec
                       )
            ],
                        style = {
                            'border': 1,
                            'font-size': size + 1,
                            "margin-bottom": 0,
                            "margin-left": 0,
                            "margin-right": "0%",
                            "margin-top": 0
                            }
        )

    dash_table_skill.layout = html.Table(
    [
        html.Thead(
            [
                #names of columns of table 
                html.Tr([
                    html.Td(["Тип"], style={"width":"11%;"}),
                    html.Td(["Сфера"], style={"width":"11%;"}),
                    html.Td(["Навык"], style={"width":"11%;"}),
                    html.Td(["Кол.вакансий"], style={"width":"11%;"}),
                    html.Td(["Даты"], style={"width":"11%;"}),
                    html.Td(["Соотношение уровней"], style={"width":"11%;"}),
                    html.Td(["Ср.зарплата"], style={"width":"11%;"}),
                    html.Td(["Зарплата по опыту работы"], )
                ])
            ],
            className = "thead-dark"
            ),
        html.Tbody(#строки таблицы
                   table_skill
                )
    ],
                style = {
                    'border': 1,
                    'font-size': size  + 1, #becouse it have different standarts, but we need same result
                    "margin-bottom": 0,
                    "margin-left": 0,
                    "margin-right": "0%",
                    "margin-top": 0
                    }
)