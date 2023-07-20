from flask import render_template, redirect, url_for, request
import pandas as pd
import requests

from . import app
from .GraphQL import schema
from .forms import QueryForm
from .dashboard import dashboards
from config import GOOGLE_API_KEY , GOOGLE_ENGINE_ID

#кастомная страница ошибки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404


#главная страница с аналитикой
@app.route('/')
def index_page():
    #будущая фича при наведении на навык открывается фрейм на страницу скилл
    dashboards()
    return render_template('index.html')


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
    #instruction https://developers.google.com/custom-search/v1/overview
    # Define the search query
    query = f"{name}:ru.wikipedia.org"

    # Set your API key
    api_key = GOOGLE_API_KEY

    # Set the search engine ID
    search_engine_id = GOOGLE_ENGINE_ID

    # Prepare the URL for the Google Search API request
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}"

    # Send a GET request to the Google Search API
    response = requests.get(url)

    # Get the JSON response
    json_response = response.json()

    # Initialize an empty list to store the URLs of relevant sites
    relevant_sites = []

    # Check if the response contains search results
    if "items" in json_response:
        # Iterate over the search results
        for item in json_response["items"][:2]:
            # Get the URL of each search result
            link = item["link"]
            # Append the URL to the list of relevant sites
            relevant_sites.append(link)
    if len(relevant_sites) >= 1 : #проверка наличии ссылки
        return render_template('description.html', url = relevant_sites[0], name = name)
    else:
        return page_not_found(f'Страницы навыка "{name}" не найдено, приносим свои извинения, просим написать о данной ошибке на почту agencyUpShot@mail.ru')