
import requests
import pandas as pd
import csv

# Определяем заголовки для запроса
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
}

# Определение параметров запроса
text = 'python'
area = '1'
params = {
    'text': text,
    'area': area,
    'page': '0'
}

# запрос на получение количества страниц
response = requests.get('https://api.hh.ru/vacancies', params=params, headers=headers)
pages_count = response.json()['pages']

# Открытие файла с ключевыми скиллами и их запись в множество
with open('key_skills1.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    keywords = []
    # set(keywords)
    for row in reader:
        keywords.append(''.join(row))


result, vacskill = [], []
# Создание dataframe для записи результатов
df = pd.DataFrame(columns={
    'id': [],
    'name': [],
    'salary': [],
    'keyskills': [],
    'area': [],
    'employer': [],
    'employementtime': []
})

# Цикл по страницам
for page in range(1):
    params['page'] = str(page)
    response = requests.get('https://api.hh.ru/vacancies', params=params, headers=headers)
    result += response.json()['items']
    
# Цикл по результатам запроса
for item in result:

    # Проверка на ключевые слова
    if 'snippet' in item and item['snippet'] is not None and 'requirement' in item['snippet'] and item['snippet']['requirement'] is not None:
        for keyword in keywords:
            if keyword in item['snippet']['requirement']:
                vacskill.append(keyword)
            elif 'key_skills' in item and item['key_skills'] is not None and keyword in item['key_skills']:
                vacskill.append(keyword)
    # set(vacskill)
    # Пересчет и проверка зп рублевой TODO: Перевод других валют в рубли(используют старые ISO 4217 коды)
    if 'salary' in item and isinstance(item['salary'], dict):
        if item['salary'].get('to') is not None and item['salary'].get('from') is not None and item['salary']['currency'] == "RUR":
            Salary = (item['salary']['to'] + item['salary']['from']) / 2
        elif item['salary'].get('from') is not None and item['salary']['currency'] == "RUR":
            Salary = item['salary']['from']
        elif item['salary'].get('to') is not None and item['salary']['currency'] == "RUR":
            Salary = item['salary']['to']
        else:
            Salary = ''         
    # Заполнение dataframe результатами
    df = df._append({
        'id': item['id'],
        'name': item['name'],
        'salary': Salary,
        'keyskills': vacskill,
        'area': item['area']['name'],
        'employer': item['employer']['name'],
        'employementtime': item['employment']['id']
        }, ignore_index=True)
   
# Сохранение результатов в csv файл
df.to_csv('db.csv', index=False, sep=';', encoding="utf-8-sig")