
# Импорт необходимых модулей
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import time

def watch():
    elapsed_time = time.time() - start_time
    mins, secs = divmod(elapsed_time, 60)
    timer = '{:02d}:{:02d}'.format(int(mins), int(secs))
    return timer
    
    
def parser(text, csvname, area):
    start_time = time.time()
    
    # Заголовки для запроса
    headers = {    
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    }
    # Параметры для получения количества страниц
    params = {    
        'text': text,    
        'area': area,    
        'page': '0',
        "only_with_salary": True
    }

    # Запрос на получение количества страниц
    response = requests.get('https://api.hh.ru/vacancies', params=params, headers=headers)
    pages_count = response.json()['pages']

    # Получение словаря, который содержит рейты обмена валюты
    apidict = requests.get('https://api.hh.ru/dictionaries').json()

    # Создание списка для результатов запроса
    result = []

    # Создание dataframe для записи результатов
    df = pd.DataFrame(columns={
        'job_title': [], 
        'level': [], 
        'min_salary': [], 
        'max_salary': [], 
        'job_requirement': [], 
        'job_description': [], 
        'employer': [], 
        'published_at': []
    })

    # Цикл по страницам
    for page in range(3):
        params['page'] = str(page)
        response = requests.get('https://api.hh.ru/vacancies', params=params, headers=headers)
        result = response.json()['items']
        
        # Цикл по результатам запроса    
        for item in result:

            print(f'Времени прошло: {watch()}, ID - {item["id"]}, Страница - {page}')

            global max_salary
            global min_salary
            min_salary = None
            max_salary = None

            # Обработка зарплаты
            # Попытаться получить информацию о зарплате из словаря item['salary']
            if item['salary'].get('to') is not None and item['salary'].get('from') is not None:
                # Если есть как минимум 'to' и 'from', получить максимальную и минимальную зарплаты
                max_salary, min_salary = (item['salary']['to'], item['salary']['from'])
            elif item['salary'].get('from') is not None:
                # Если есть только 'from', записать значение в min_salary
                min_salary = item['salary']['from']
            elif item['salary'].get('to') is not None:
                # Если есть только 'to', записать значение в max_salary
                max_salary = item['salary']['to']
            else:
                max_salary, min_salary = '', ''

                    
            # Получение курса валюты
            if type(min_salary) is int:
                for currency in apidict['currency']:
                    if currency['code'] == item['salary']['currency']:
                        currency_rate = 1/currency['rate']
                min_salary = min_salary * currency_rate
            elif type(max_salary) is int:
                for currency in apidict['currency']:
                    if currency['code'] == item['salary']['currency']:
                        currency_rate = 1/currency['rate']
                max_salary = max_salary * currency_rate

            
            # Обработка должности
            job_title = item['name'].lower()
            if 'intern' in job_title or 'стажер' in job_title:
                level = 'intern'
            elif 'junior' in job_title:
                level = 'junior'
            elif 'middle' in job_title:
                level = 'middle'
            elif 'senior' in job_title:
                level = 'senior'
            elif 'lead' in job_title:
                level = 'lead'
            else:
                level = ''
            
            employer = item['employer']['name']
            
            # Обработка описания вакансии
            global job_requirement
            vacancy = requests.get(item['url']).json()
            if 'errors' in vacancy:
                print(vacancy['errors'][0]['captcha_url']+'&backurl=')
                time.sleep(20)
            vacancy = requests.get(item['url']).json()
            job_requirement = ''
            if 'key_skills' in vacancy:
                job_requirement = [skill['name'] for skill in vacancy['key_skills']]
                job_requirement = ','.join(str(x)for x in job_requirement)
            job_description = ''
            if 'description' in vacancy:
                job_description = vacancy['description']
                job_description = re.sub('<.*?>', '', job_description)
            published_at = item['published_at'].split('T')[0]
            url = 'https://hh.ru/vacancy/'+item['id']
            vacresponse = requests.get(url)
            soup = BeautifulSoup(vacresponse.content, 'html.parser')
            rate_element = soup.find('div',{'data-qa':'employer-review-small-widget-total-rating'})
            if rate_element is not None:
                employer_rating = rate_element.text.strip()
            else:
                employer_rating = ''


            # Добавление результатов в dataframe
            df = df._append({
                'job_title': job_title,
                'level': level,
                'min_salary': min_salary,
                'max_salary': max_salary,
                'job_requirement': job_requirement,
                'job_description': job_description,
                'employer': employer,
                'employer_rating': employer_rating,
                'published_at': published_at
            }, ignore_index=True)

    # Запись результатов в csv файл
    df.to_csv(str(csvname)+'.csv', index=False, sep=';', encoding='utf-8-sig') 

    
parser('python', 'pythonfullvac', '1')
