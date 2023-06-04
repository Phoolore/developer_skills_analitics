
import requests
import pandas as pd
import csv

# Заголовки для запроса
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
}

# Параметры запроса
text = 'python'
area = '1'

# Параметры для получения количества страниц
params = {
    'text': text,
    'area': area,
    'page': '0'
}

# Запрос на получение количества страниц
response = requests.get('https://api.hh.ru/vacancies', params=params, headers=headers)
pages_count = response.json()['pages']

# Получение словаря, который содержит рейты обмена валюты
apidict = requests.get('https://api.hh.ru/dictionaries').json()

# Открытие файла с ключевыми скиллами и запись их в множество
with open('key_skills1.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    keywords = []
    for row in reader:
        keywords.append(''.join(row))
skilldf = pd.DataFrame({
    'skills': keywords,
    'amount': 0,
    'salarysum': 0
})


# Создание списка для результатов запроса
result = []

# Создание dataframe для записи результатов
df = pd.DataFrame(columns={
    'id': [],
    'name': [],
    'salary': [],
    'keyskills': [],
    'area': [],
    'experience': [],
    'employementtime': []
})

# Цикл по страницам
for page in range(pages_count):
    params['page'] = str(page)
    response = requests.get('https://api.hh.ru/vacancies', params=params, headers=headers)
    result += response.json()['items']
    
    # Цикл по результатам запроса
    for item in result:
        vacskill = []
        
        # Получение средней зарплаты
        if 'salary' in item and isinstance(item['salary'], dict):
            if item['salary'].get('to') is not None and item['salary'].get('from') is not None:
                Salary = (item['salary']['to'] + item['salary']['from']) / 2
            elif item['salary'].get('from') is not None:
                Salary = item['salary']['from']
            elif item['salary'].get('to') is not None:
                Salary = item['salary']['to']
            else:
                Salary = ''
            for currency in apidict['currency']:
                if currency['code'] == item['salary']['currency']:
                    Salary = Salary * (1/currency['rate'])
                    
        # Получение информации о рабочих днях и интервалах
        if isinstance(item['working_days'], dict):
            working_days_id = item['working_days']['0']['id']
        else:
            working_days_id = ''
        if isinstance(item['working_time_intervals'], dict):
            working_time_intervals_id = item['working_time_intervals']['0']['id']
        else:
            working_time_intervals_id = ''
            
        # Проверка на ключевые слова
        if item['snippet'] is not None and 'requirement' in item['snippet'] and item['snippet']['requirement'] is not None:
            for keyword in keywords:
                if keyword in item['snippet']['requirement']:
                    vacskill.append(keyword)                            
                elif 'key_skills' in item and item['key_skills'] is not None and keyword in item['key_skills']:
                    vacskill.append(keyword)
                    
        # Заполнение dataframe результатами
        for skill in vacskill:
            skilldf.loc[skilldf['skills'] == skill, 'amount'] += 1           
            skilldf.loc[skilldf['skills'] == skill, 'salarysum'] += Salary*(1/len(vacskill))
        df = df._append({
            'id': item['id'],
            'name': item['name'],
            'salary': Salary,
            'keyskills': vacskill,
            'area': item['area']['id'],
            'experience': item['experience'].get('id'),
            'employementtime': item['employment']['id'],
            'workingdays': working_days_id,
            'workingintervals': working_time_intervals_id
        }, ignore_index=True)

# Расчет средней зарплаты по каждому скиллу и запись в csv файл
skilldf['value'] = skilldf['salarysum'] / skilldf['amount'].replace(0, 1)
skilldf.to_csv('db2.csv', index=False, sep=';', encoding='utf-8-sig')

# Запись результатов в csv файл
df.to_csv('db1.csv', index=False, sep=';', encoding='utf-8-sig')