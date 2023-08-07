import pandas as pd
import numpy as np
from math import pi

from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Legend, LegendItem, LabelSet, RangeTool, HoverTool, DatetimeTickFormatter, WheelZoomTool, WheelPanTool, UndoTool, RedoTool, ResetTool, SaveTool


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


def LevelPie(df_full):
    df = counts(df_full, "experience")
    
    #Источник данных
    df = counts(df_full, "experience")
    
    # Задаем значения для диаграммы
    value = df["counts"].tolist()

    # Создаем словарь с данными
    data = {
        'name': df["experience"].tolist(),  # Метки для каждого сектора
        'value': value,  # Значения для каждого сектора
        'angle': [v/sum(value)*2*pi for v in value],  # Угол для каждого сектора
        'cumulative_angle':[(sum(value[0:i+1])- (item/2))/sum(value)*2*pi for i,item in enumerate(value)],  # Кумулятивный угол для каждого сектора
        'percentage': [d/sum(value)*100 for d in value],  # Процент для каждого сектора
        'color': colors[:len(value)]  # Цвет для каждого сектора
    }

    # Создаем метки в процентах
    data['label'] = ["{:.0f}%".format(p) for p in data['percentage']]

    # Вычисляем координаты для меток
    data['cos'] = np.cos(data['cumulative_angle'])*0.3
    data['sin'] = np.sin(data['cumulative_angle'])*0.3

    # Создаем источник данных для Bokeh
    source = ColumnDataSource(data=data)

    # Настройки для всплывающих подсказок
    TOOLTIPS = [
        ("Value", "@value"),  # Значение сектора
        ("Percentage", "@percentage{0.2f}%")  # Процент сектора
    ]

    # Создаем объект Figure для построения графика
    fig = figure(height=600,width=600,x_range=(-1,1), y_range=(-1,1), tools='hover', tooltips=TOOLTIPS, toolbar_location=None)
    
    # Создаем кольцевые секторы диаграммы
    r = fig.annular_wedge(x=0, y=0, inner_radius=0.2, outer_radius=0.4,
                        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                        fill_color='color', fill_alpha=1, direction = 'anticlock', line_alpha = 1, line_color = "black", line_width = 5,
                        source=source)

    # Создаем легенду
    legend = Legend(items=[LegendItem(label=dict(field="name"), renderers=[r])], location=(0, 80), label_text_font_size = str(size) + "px")
    legend.background_fill_alpha = 0
    legend.border_line_alpha = 0
    fig.add_layout(legend, 'right')

    # Добавляем метки
    labels = LabelSet(x='cos', y='sin', text="label", y_offset=0,
                      text_font_size = str(size) + "px", text_color="black",
                      source=source, text_align='center')
    fig.add_layout(labels)

    # Настраиваем внешний вид графика
    fig.axis.axis_label=None
    fig.axis.visible=False
    fig.grid.grid_line_color = None
    fig.outline_line_color = None
    fig.background_fill_alpha = 0
    fig.border_fill_alpha = 0
    
    #Настраиваем интерактивную легенду
    fig.legend.click_policy="hide"

    
    html = file_html(fig, CDN, "my plot")
    
    return html