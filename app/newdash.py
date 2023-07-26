from dash import html, dcc
import pandas as pd
import plotly.graph_objects as go

from . import app, superpage
from .GraphQL import schema

size = 10 #размер текста на графиках
missing = 0 #замена для пустых клеток
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']


def counts_table(name, df):
    counts_table = []
    for i, row in df.groupby(name)[name].count().rename("counts").reset_index().iterrows():
        counts_table += [html.Tr([
            html.Th(row[name]),
            html.Th( row['counts'])
        ])] 
    return counts_table


def avg_sal(df):
    avg = int(((df['min_salary'] + df['min_salary'])/2).mean())
    return avg


def navbar():
    layout = html.Div([
        html.A("Главная", href = '/')
        ], className = "navbar")
    return layout


def footer():
    layout = html.Div([
        html.P([
            "Рабочая почта: agencyUpShot@mail.ru", html.Br(),
          "2023 Аналитика. Спасибо за внимание!!!"
        ])
        ], className = "footer", id = "footer")
    return layout


def side_navbar():
    layout = html.Div([
        html.A("Главная", href = "/"),
        html.A("GraphQL", href = "/graphql/")
        ], className = "sidebar")
    return layout


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
        margin=dict(l=2, r=2, t=3, b=3),
        plot_bgcolor='rgba(255, 255, 255, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0)',
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
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0)',
        xaxis={'gridcolor': 'rgba(0, 0, 0, 256)'},  # Изменение цвета разметки на черный
        yaxis={'title': 'Кол.вакансий', 'gridcolor': 'rgba(0, 0, 0, 256)'},  # Изменение цвета разметки на черный
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
        hovermode='closest',
        plot_bgcolor='rgba(255, 255, 255, 0)',  # Цвет фона
        paper_bgcolor='rgba(255, 255, 255, 0)',  # Цвет фона графика
        margin=dict(l=0, r=0, t=0, b=0),#отступы
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
        font = dict(
            size = size
        )
        )
    return fig



def dashboards(spec = None, skill = None):
    mode = ["Специализации","Навыки"][0]
    rows = [] #хранитель строк будущего df с вакансиями
    with app.app_context():
        query = '{getSpecializations{ edges { node {name, vacancies {edges { node {name, minSalary, maxSalary, experience, keySkills, publishedAt, status, city} } } } } } }' #Запрос к GraphQL для получения специализаций и прокрепленных к ним ваканиям
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
                    'status' : vac['node']['status'],
                    'city' : vac['node']['city']
                    }]

    df_full = pd.DataFrame(rows, index = [i for i in range(len(rows))]).fillna(missing)#полный df для специализаций и скиллов
    with open("data.txt", "w+") as f:
        f.write(df_full.to_json())
    df_spec = df_full.loc[df_full['status']] #Заготовка для будущих фильтров специализаций
    df_skill = df_full.loc[df_full['status']] #Заготовка для будущих фильтров специализаций
    
    cities_list = df_full['city'].unique().tolist().remove(missing)
    filter_list = [] #хранитель вариантов для фильтров
    table_spec = [] #хранитель строк таблицы специализаций
    table_skill = [] #хранитель строк таблицы навыков

    if len(df_full) > 0:
        for i, spec in enumerate(df_spec['specialization'].unique()):#перебор специализаций
            df = df_spec[df_spec['specialization'] == spec] #выборка по специализации
            
            if mode == "Специализации":
                filter_list += [{"label": spec, "value": spec}]
            table_spec += [
                html.Tr([
                    html.Td(["ИТ"]),
                    html.Td([spec]),
                    html.Td([len(df)]),
                    
                    html.Td([dcc.Graph(
                    id='dateline_spec' + str(i + 1),
                    config={"locale": 'ru'},
                    figure=dateline(df, spec),
                    )]),
                    
                    html.Td([dcc.Graph(
                    id='levelpie_spec'+ str(i + 1),
                    config={"locale": 'ru'},
                    figure=levelpie(df),
                    )]),
                    
                    html.Td(avg_sal(df)),
                    
                    html.Td([dcc.Graph(
                    id='salbox_spec'+ str(i),
                    config={"locale": 'ru'},
                    figure = salbox(df),

                    )])
                ])
            ]

        for skills_packs in df_skill['key_skills'].unique(): #получение наборов навыков из вакансий без повторений
            for i, skill in enumerate(skills_packs.replace("[", "").replace("]", "").split(','))  :#перебор навыков
                df = df_skill[df_skill['key_skills'].str.contains(skill)] #выборка вакансий с навыком
                
                if mode == "Навыки":
                    filter_list += [{"label": skill, "value": skill}]
                    
                table_skill += [
                    html.Tr([
                        html.Td(["ИТ"]),
                        html.Td([skill]),
                        html.Td([len(df)]),
                        html.Td([dcc.Graph(
                            id='dateline_skill' + str(i + 1),
                            config={"locale": 'ru'},
                            figure=dateline(df, skill)
                            )]),
                            
                            html.Td([dcc.Graph(
                            id='levelpie_skill'+ str(i + 1),
                            config={"locale": 'ru'},
                            figure=levelpie(df)
                            )]),
                            
                            html.Td(avg_sal(df)),
                            
                            html.Td([dcc.Graph(
                            id='salbox_skill'+ str(i),
                            config={"locale": 'ru'},
                            figure = salbox(df)
                            )])
                    ])
                ]

    # localization
    superpage.scripts.append_script({"external_url": "https://cdn.plot.ly/plotly-locale-ru-latest.js"})

    table_spec_layout = html.Div([
        html.Table(
            html.Thead(
                #names of columns of table 
                html.Tr([
                    html.Td(["Сфера"]),
                    html.Td(["Название"]),
                    html.Td(["Кол.вакансий"]),
                    html.Td(["Даты"], style={"width":"20%;"}),
                    html.Td(["Соотношение уровней"], style={"width":"20%;"}),
                    html.Td(["Ср.зарплата"]),
                    html.Td(["Зарплата по опыту работы"], style={"width":"40%;"})
                    ]), 
                className = "thead-dark"),
            style = {
                'width': "100%",
                'border': 1,
                'font-size': size  + 1, #becouse it have different standarts, but we need same result
                "margin-bottom": 0,
                "margin-left": 0,
                "margin-right": 0,
                "margin-top": 0
                }),
        html.Div(html.Table(html.Tbody(
            table_spec
            )), className = "scroll-table-body")
            
            ], className="scroll-table")

    table_skill_layout = html.Div([
        html.Table(
            html.Thead(
                #names of columns of table 
                html.Tr([
                    html.Td(["Сфера"]),
                    html.Td(["Название"]),
                    html.Td(["Кол.вакансий"]),
                    html.Td(["Даты"], style={"width":"20%;"}),
                    html.Td(["Соотношение уровней"], style={"width":"20%;"}),
                    html.Td(["Ср.зарплата"]),
                    html.Td(["Зарплата по опыту работы"], style={"width":"40%;"})
                    ]), 
                className = "thead-dark"),
            style = {
                'width': "100%",
                'border': 1,
                'font-size': size  + 1, #becouse it have different standarts, but we need same result
                "margin-bottom": 0,
                "margin-left": 0,
                "margin-right": 0,
                "margin-top": 0
                }),
        html.Div(html.Table(html.Tbody(
            table_skill
            )), className = "scroll-table-body")
            
            ], className="scroll-table")

    vacancies = html.Div([
        html.Div([
        html.H3("Вакансий"), html.Br(), html.H3(len(df_full))
        ], className = "col-7"),
        html.Div([
        dcc.Graph(id='dateline_full', config={"locale": 'ru'}, figure=dateline(df_full, "Общий"))
        ], className = "col-5")
        ], className = "row", id = "Vacancies_graph")
    salaries = html.Div([
        html.Div([
        html.H3("Средняя зарплата"), html.Br(), 
        html.H3((avg_sal(df_full), " Руб.")), html.Br(), 
        html.Div(html.H4(["Минимум:", ((df_full.loc[df_full['min_salary'] != missing])['min_salary']+(df_full.loc[df_full['max_salary'] != missing])['max_salary']).min(), " Руб."])), html.Br(), 
        html.Div(html.H4(["Максимум:", ((df_full.loc[df_full['min_salary'] != missing])['min_salary']+(df_full.loc[df_full['max_salary'] != missing])['max_salary']).max(), " Руб."]))
        ], className = "col-7"),
        html.Div([
        dcc.Graph(id='salbox_full', config={"locale": 'ru'}, figure=salbox(df_full))
        ], className = "col-5")
        ], className = "row", id = "Salaries_graph")
    levels = html.Div([html.Div([
        html.Div([html.H3("Соотношение уровней"), html.Br(),
                  html.Table(
                      [
                          html.Tbody(#строки таблицы
                                     counts_table("experience", df_full)
                                     )
                    ], className = "thead-dark", 
                      style = {
                            'width': "100%",
                            'font-size': size + 1,
                            })   
                  ])
    ], className = "col-5"),
        html.Div([
        dcc.Graph(id='levelpie_full', config={"locale": 'ru'}, figure=levelpie(df_full))
        ], className = "col-7")
        ], className = "row", id = "Levels_graph")
    timetable = html.Div([
        html.H3("Text"),
        html.Table(
        [
            
            html.Tbody(#строки таблицы
                    [
                       html.Tr([
                        html.Th(["Тип"]),
                        html.Th(["Кол.вакансий"]),
                        html.Th(["Ср.зарплата"]),
                        ])
                    ], className = "thead-dark")
                
                       
            ],
                        style = {
                            'width': "100%",
                            'font-size': size + 1,
                            }
        )


        ], id = "Timetable_graph")
    cities = html.Div([
        html.H3("Graph"),
        html.Table(
        [
            
            html.Tbody(#строки таблицы
                    [
                       html.Tr([
                        html.Th(["Город"]),
                        html.Th(["Кол.вакансий"]),
                        html.Th(["Ср.зарплата"]),
                        ])
                    ], className = "thead-dark")
                
                       
            ],
                        style = {
                            'width': "100%",
                            'font-size': size + 1,
                            }
        )


        ], id = "Cities_graph")
    
    layout = [
        html.Div([
            html.Div(html.H1("Заголовок"), className = "col-10"),
            html.Div(html.Button("Настройки", id = "settings-button"), className = "col-2"),
            ], className = "row"),
        html.Div([
            html.Div([html.Div("Режим", className = "col-4"),html.Div(dcc.RadioItems(options = ["Специализации", "Навыки"], value = "Специализации", id="Mode", inline = True), className = "col-8")], className = "row", style={"width": "100%"}),
            html.Div([html.Div("Фильтры", className = "col-4"),html.Div(dcc.Dropdown(filter_list, filter_list, multi=True, placeholder="Выберете фильтры",  id = "Filters"), className = "col-8")], className = "row", style={"width": "100%"}),
            html.Div([html.Div("Промежуток времени", className = "col-4"),html.Div(dcc.DatePickerRange(min_date_allowed = df_full["published_at"].min(), start_date=df_full["published_at"].min(), max_date_allowed = df_full["published_at"].max(), end_date = df_full["published_at"].max(), id='date-range'), className = "col-8")], className = "row", style={"width": "100%"}),
            html.Div([html.Div("Фильтр слов в названии вакансии", className = "col-4"),html.Div(dcc.Input(placeholder='Напишите слово-фильтр...', type='text', value='', debounce=True, min=2, step=1), className = "col-8")], className = "row", style={"width": "100%"}),
            html.Div([html.Div("Тёмная/Светлая тема", className = "col-4"),html.Div(html.Button("Кнопка"), className = "col-8")], className = "row", style={"width": "100%"}),
            html.Div([html.Div("Города", className = "col-4"),html.Div(dcc.Dropdown(cities_list, cities_list, multi=True, placeholder="Выберете города",  id = "Cities"), className = "col-8")], className = "row", style={"width": "100%"}),
            html.Div([html.Div("Показывать вакансии из архива", className = "col-4"),html.Div(html.Button("Кнопка"), className = "col-8")], className = "row", style={"width": "100%"}),
            
            ], id  = "settings-div"),
        html.Div([
            html.Div([
                table_spec_layout,
                table_skill_layout
                ], className = "col-7"),
            html.Div([
                vacancies,
                salaries,
                levels,
                timetable,
                cities
                ], className = "col-5")
            ], className = "row", id = "Dashboards", style={"width": "100%"})
    ]
    return layout


def layout():
    layout = html.Div([
        navbar(),
        html.Div([
            html.Div(dashboards(), className = "col-10"),
            html.Div(side_navbar(), className = "col-2")
        ], className = "row"),
        footer()
    ])
    return layout


superpage.layout = layout()