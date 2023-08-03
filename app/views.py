from flask import render_template, redirect, url_for, request
import pandas as pd
import numpy as np
import requests

from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool, HoverTool, DatetimeTickFormatter, WheelZoomTool, WheelPanTool, UndoTool, RedoTool, ResetTool, SaveTool

from . import app
from .GraphQL import schema
from .forms import QueryForm

size = 10 #размер текста на графиках
missing = 0 #замена для пустых клеток
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']


def avg_sal(df, df_bool = False):
    """Вспомогательная функция получения ср.зп"""
    if df_bool == True: #Режим возврата массива
        return (df['min_salary'] + df['max_salary'])/2
    avg = int(((df['min_salary'] + df['max_salary'])/2).mean())
    return avg


def counts(df_full, name):
    """Вспомогательная функция упорядочивания df по колл. вакансий в зависимости от столбца для группировки"""
    df = df_full.loc[df_full[name] != missing]
    df = df.groupby(name)[name].count().rename("counts").reset_index()
    
    return df


#кастомная страница ошибки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404


#страница запросов GraphQL
@app.route('/graphql/', methods=['GET', 'POST'])
def graphql_query_page():
    query = '{getSpecializations{ edges { node {name, vacancies {edges { node {name, minSalary, maxSalary, experience, publishedAt} } } } } } }' #Запрос к GraphQL для получения специализаций и прокрепленных к ним ваканиям
    result = schema.execute(query)
    with open("data.txt", "w+") as f:
        f.write(str(result))
    if request.method == 'POST':
        query = request.form['query']
    else:
        query = ''
    form = QueryForm()
    result = schema.execute(query)
    data = result.data
    errors = result.errors
    return render_template('graphql.html', data = data, query = query, errors = errors, form = form)


#страница подробностей о навыке
@app.route('/description/<string:name>')
def description_page(name):
    url = f'https://ru.wikipedia.org/w/index.php?search={name}'#ссылка на ресурс
    if "Результаты поиска" not in requests.get(url).content: #Проверка что сайт найден
        return render_template('description.html', url = url, name = name)
    else:
        return page_not_found(f'Страницы навыка "{name}" не найдено, приносим свои извинения, просим написать о данной ошибке на почту agencyUpShot@mail.ru')


def DateLine(df_full):
    """График DateLine типа scatter для дат по кол. вакансий за день"""
    color = "orange"
    background_color = "#efefef"
    y_label = "Вакансий опубликованно за день"

    # Создание источника данных
    df = counts(df_full, "published_at")
    dates = np.array(pd.to_datetime(df["published_at"]), dtype=np.datetime64)
    source = ColumnDataSource(data=dict(date=dates, y = df["counts"]))
    
    # Создание графика
    fig = figure(height=300, width=800, background_fill_color=background_color, #визуальные настройки
                 tools = [], toolbar_location="right",x_axis_type="datetime", x_axis_location="below",x_range=(dates.min(), dates.max())) #настройки
    
    # Панель инструментов
    zoom = WheelZoomTool(dimensions="width", name = "Увеличение", description = "Увеличить по оси x")
    fig.add_tools(zoom)
    fig.add_tools(WheelPanTool(dimension = "width", name = "Передвижение", description = "Передвижение по оси x"))
    fig.add_tools(UndoTool(name = "Назад", description = "Отменить действие"))
    fig.add_tools(RedoTool(name = "Вперёд", description = "Вернуть действие"))
    fig.add_tools(ResetTool(name = "Сброс", description = "Сброс до начального положения"))
    fig.add_tools(SaveTool(name = "Сохранить", description = "Сохранить текущий график как картинку"))
    
    # Активные инструменты
    fig.toolbar.active_drag = None
    fig.toolbar.active_scroll = zoom
    
    #Hover
    hover = HoverTool(tooltips=[("Дата", "$x{%d/%m/%Y}"), ("Вакансий опубликованно за день", "$y{0}")], formatters={"$x": "datetime"}, name = "Описание", description = "Показывать описание точек")
    fig.add_tools(hover)
    
    #Форматирование дат оси x
    fig.xaxis.formatter = DatetimeTickFormatter(hours="%H:%M", days="%d/%m", months="%m/%y", years="%Y")
    
    #Элементы и визуализация графика
    fig.scatter('date', 'y', source=source, 
                size=10, color='black', line_color = color, line_width = 3, alpha=1, level = "overlay") #визуальные настройки
    fig.line('date', 'y', source=source,
            line_color = color, line_width = 5)#визуальные настройки
    fig.yaxis.axis_label = y_label
    fig.toolbar.autohide = True
    fig.background_fill_alpha = 0
    fig.border_fill_alpha = 0
    fig.grid.grid_line_color = "black"  # Цвет сетки - черный
    fig.grid.grid_line_alpha = 0.8  # Прозрачность сетки - яркая
    fig.outline_line_alpha = 1
    fig.outline_line_color = "black"

    #Создание ползунка
    select = figure(height=130, width=800, y_range=fig.y_range,
                    x_axis_type="datetime", y_axis_type=None,
                    tools="", toolbar_location=None, background_fill_color=background_color)

    range_tool = RangeTool(x_range=fig.x_range)
    range_tool.overlay.fill_color = "green"
    range_tool.overlay.fill_alpha = 0.3
    
    #Настрока элементов ползунка и визуализации
    select.scatter('date', 'y', source=source, 
                size=10, color='black', line_color = color, line_width = 3, alpha=1, level = "overlay") #визуальные настройки
    select.line('date', 'y', source=source,
                line_color = color, line_width = 5)#визуальные настройки
    select.add_tools(range_tool)
    select.background_fill_alpha = 0
    select.border_fill_alpha = 0
    select.grid.grid_line_color = "black"  # Цвет сетки - черный
    select.grid.grid_line_alpha = 0.8  # Прозрачность сетки - яркая
    select.outline_line_alpha = 1
    select.outline_line_color = "black"
    
    html = file_html(column(fig, select), CDN, "my plot")
    
    return html


@app.route("/", methods=['GET', 'POST'])
def index_page():
    """Построение графиков и упаковка в html"""
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
    cities_list = df_full['city'].unique().tolist().remove(missing)
    filter_list = [] #хранитель вариантов для фильтров

    return render_template("index.html", 
                           GeneralDateLine = DateLine(df_full)
                           )

