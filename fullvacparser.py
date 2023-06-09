
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import time
start_time = time.time()
#Секундомер | Stopwatch
def watch():
    elapsed_time = time.time() - start_time
    mins, secs = divmod(elapsed_time, 60)
    timer = '{:02d}:{:02d}'.format(int(mins), int(secs))
    return timer

def parser(text, csvname, area='1', pages=None):
    # Заголовки для запроса | Headers for request
    headers = {    
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    }
    # Параметры для получения количества страниц | Parameters to get the number of pages
    params = {    
        'text': text,    
        'area': area,    
        'page': '0',
        "only_with_salary": True
    }

    # Запрос на получение количества страниц | Request to get the number of pages
    response = requests.get('https://api.hh.ru/vacancies', params=params, headers=headers)
    pages_count = response.json()['pages']
    if pages is None:
        pages = pages_count

    # Получение словаря, который содержит рейты обмена валюты | Getting the dictionary, which contains currency exchange rates
    apidict = requests.get('https://api.hh.ru/dictionaries').json()

    # Создание списка для результатов запроса | Creating a list for request results
    result = []

    # Создание dataframe для записи результатов | Creating a dataframe for recording results
    df = pd.DataFrame(columns={
        'job_title': [], 
        'level': [], 
        'min_salary': [], 
        'max_salary': [], 
        'job_req': [], 
        'job_desc': [], 
        'employer': [], 
        'published_at': []
    })

    # Цикл по страницам | Page cycle
    for page in range(pages):
        params['page'] = str(page)
        response = requests.get('https://api.hh.ru/vacancies', params=params, headers=headers)
        result = response.json()['items']
        
        # Цикл по результатам запроса | Cycle by every result in request
        for item in result:

            print(f'Времени прошло: {watch()}, ID - {item["id"]}, Страница - {page}')

            global max_salary
            global min_salary
            min_salary = None
            max_salary = None

            # Обработка зарплаты | Processing salary
            # Попытаться получить информацию о зарплате из словаря item['salary'] | Try to get salary information from the item['salary'] dictionary 
            if item['salary'].get('to') is not None and item['salary'].get('from') is not None:
                # Если есть как минимум 'to' и 'from', получить максимальную и минимальную зарплаты | If there are at least 'to' and 'from', get the maximum and minimum salary 
                max_salary, min_salary = (item['salary']['to'], item['salary']['from'])
            elif item['salary'].get('from') is not None:
                # Если есть только 'from', записать значение в min_salary | If there is only 'from', write the value in min_salary
                min_salary = item['salary']['from']
            elif item['salary'].get('to') is not None:
                # Если есть только 'to', записать значение в max_salary | If there is only 'to', write the value in max_salary
                max_salary = item['salary']['to']
            else:
                max_salary, min_salary = '', ''

                    
            # Получение курса валюты | Exchange Rate
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

            
            # Обработка должности | Vacancy title check
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
            
            # Обработка описания вакансии | Processing each vacancy from id, not from 'search by name'
            global job_req
            vacancy = requests.get(item['url']).json()

            #ПРОВЕРКА КАПЧИ, 20 СЕКУНД ЧТОБЫ ПЕРЕЙТИ ПО ССЫЛКЕ И РЕШИТЬ |  CAPTCHA, 20 SECONDS TO FOLLOW LINK AND SOLVE
            if 'errors' in vacancy:
                print(vacancy['errors'][0]['captcha_url']+'&backurl=')
                time.sleep(20)
            #обновление json вакансии, если капча пройдена | vacancy json update, if the captcha is passed 
            vacancy = requests.get(item['url']).json()
            #Проверка скиллов | Key skills check
            job_req = ''
            if 'key_skills' in vacancy:
                job_req = [skill['name'] for skill in vacancy['key_skills']]
                job_req = ','.join(str(x)for x in job_req)
            #Проверка описания | Description check
            job_desc = ''
            if 'description' in vacancy:
                job_desc = vacancy['description']
                job_desc = re.sub('<.*?>', '', job_desc)
            #Проверка даты | Date check
            published_at = item['published_at'].split('T')[0]
            #Проверка рейтинга | Employer rating check
            url = 'https://hh.ru/vacancy/'+item['id']
            vacresponse = requests.get(url)
            soup = BeautifulSoup(vacresponse.content, 'html.parser')
            rate_element = soup.find('div', {'data-qa':'employer-review-small-widget-total-rating'})  #скорее всего здесь проблемы, пока не понял в чем
            if rate_element is not None:
                employer_rating = rate_element.text.strip()
            else:
                employer_rating = ''


            # Добавление результатов в dataframe | updating dataframe with results
            df = df._append({
                'job_title': job_title,
                'level': level,
                'min_salary': min_salary,
                'max_salary': max_salary,
                'job_req': job_req,
                'job_desc': job_desc,
                'employer': employer,
                'employer_rating': employer_rating,
                'published_at': published_at
            }, ignore_index=True)

    # Запись результатов в csv файл | dataframe to csv file
    df.to_csv(str(csvname)+'.csv', index=False, sep=';', encoding='utf-8-sig') 

    
parser('python', 'pythonfullvac', '1', 6)