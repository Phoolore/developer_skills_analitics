import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup
import time
import requests
import csv
# from . import app
# from .GraphQL import schema


start_time = time.time()
url = 'https://api.hh.ru/vacancies/'
def watch():
    elapsed_time = time.time() - start_time
    mins, secs = divmod(elapsed_time, 60)
    timer = '{:02d}:{:02d}'.format(int(mins), int(secs))
    return timer

access_token = 'APPLV743VFT8SPNGUR1CDAPRMF80BPVD18OSU0J47NIUHRPULIS82R2GDEQLOFB6'

headers = {
    'User-Agent': "online python programmer's skills analysis(agencyUpShot@mail.ru)",
    'Authorization': f"Bearer {access_token}"
} 

apidict = requests.get('https://api.hh.ru/dictionaries').json()


def create_csv(filename, data):
    """
    The function `create_csv` takes a filename and data as input, and creates a CSV file with the given
    filename containing the data.
    
    :param filename: The filename parameter is a string that specifies the name of the CSV file that
    will be created. It should include the file extension ".csv"
    :param data: The "data" parameter is a list of lists. Each inner list represents a row in the CSV
    file, and each element in the inner list represents a cell in that row
    """
    with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerows(data)
        
csvdata = [['vId', 'name', 'city', 'minSalary', 'maxSalary',
        'experience', 'schedule', 'employment', 'description',
        'keySkills', 'employer', 'publishedAt', 'specializationId']]


async def parse(id):
    """
Функция  `parse`  принимает в качестве входного 
параметра идентификатор (ID), выполняет запрос к API для
получения данных и разбирает ответ, чтобы извлечь
соответствующую информацию, такую как название вакансии,
зарплата, город, уровень опыта, график работы, тип занятости, описание, ключевые навыки, идентификатор работодателя,
дата публикации и идентификатор специализации.
:param id: Параметр  `id`  является уникальным идентификатором вакансии.
Он используется для получения деталей конкретной вакансии из API.
    """
         
    vacurl = url + id
    async with aiohttp.ClientSession() as session:
        async with session.get(vacurl, headers=headers) as response:
            vacdata = await response.json()

            name = vacdata['name']
            for cur in apidict['currency']:
                if cur['code'] == vacdata['salary']['currency']:
                    currency_rate = 1/cur['rate']
            minSalary = vacdata['salary']['from']
            if minSalary is None:
                minSalary = ''
            else:
                minSalary*= currency_rate
                minSalary = int(minSalary)
            maxSalary = vacdata['salary']['to']
            if maxSalary is None:
                maxSalary = ''
            else:
                maxSalary*= currency_rate
                maxSalary = int(maxSalary)
            city = vacdata['area']['id']
            experience = vacdata['experience']['id']
            schedule = vacdata['schedule']['id']
            employment = vacdata['employment']['id']
            description = re.sub('<.*?>', '', vacdata['description'])
            if 'key_skills' in vacdata:
                keySkills = [skill['name'] for skill in vacdata['key_skills']]
                keySkills = ','.join(str(x) for x in keySkills)
                keySkills = keySkills.lower()
            else:
                keySkills = ''
            
            employer = vacdata['employer'].get('id')
            if employer is None:
                employer = ''
            publishedAt = vacdata['published_at'].split('T')[0]
            specializationId = vacdata['professional_roles'][0]['id']
            vac = [id, name, city, minSalary, maxSalary, experience,
                   schedule, employment, description, keySkills,
                   employer, publishedAt, specializationId]
            csvdata.append(vac)
            
            # with app.app_context():
            #     query = '{getSpecializations{ edges { node {name, vacancies {edges { node {name, minSalary, maxSalary, experience, keySkills, publishedAt} } } } } } }' #Запрос к GraphQL для получения специализаций и прокрепленных к ним ваканиям
            #     query = query.replace("name", name)
            #     query = query.replace("minSalary", minSalary)
            #     query = query.replace("maxSalary", maxSalary)
            #     query = query.replace("experience", experience)
            #     query = query.replace("keySkills", keySkills)
            #     query = query.replace("publishedAt", publishedAt)
            #     data = schema.execute(query).data

    
async def main(per_page, required_pages=None, area='113', searchtext=''):
    """
Функция  `main`  принимает параметры для количества элементов на странице,
требуемого количества страниц, кода области и текста поиска, и выполняет определенные действия.
:param per_page: Количество результатов, отображаемых на одной странице
:param required_pages: Параметр  `required_pages`  является необязательным
и определяет количество страниц результатов, которые вы хотите получить.
Если вы не указываете значение для этого параметра, он по умолчанию принимает значение  `None`,
что означает получение всех доступных страниц.
:param area:  Параметр  `area`  используется для указания географической области поиска. Это строка,
которая представляет код или название местоположения. Значение по умолчанию - '113', Россия.
:param searchtext: Параметр  `searchtext`  является строкой, которая представляет текст,
который вы хотите найти. Он используется для фильтрации результатов на основе ключевого слова или фразы для поиска на HH.ru.
    """
    params = {    
        'text': searchtext,    
        'area': str(area),    
        'page': '0',
        "only_with_salary": True,
        'per_page': str(per_page)
    }
        
    response = requests.get(url, params=params, headers=headers)
    pages_count = response.json()['pages']
    if required_pages is None:
        required_pages = pages_count
        
    for page in range(required_pages):
        params['page'] = str(page)
        response = requests.get(url, params=params, headers=headers)
        result = response.json()['items']
        
        for item in result:
            id = item['id']
            await parse(id)
            
asyncio.run(main(100, 19, 113, 'python'))

csvname = 'test05.csv'
create_csv(csvname, csvdata)
print(f'deltaTime: {watch()}, CSV - {csvname}')

# 0	
# id	"156"
# name	"BI-аналитик, аналитик данных"
# 1	
# id	"160"
# name	"DevOps-инженер"
# 2	
# id	"10"
# name	"Аналитик"
# 3	
# id	"12"
# name	"Арт-директор, креативный директор"
# 4	
# id	"150"
# name	"Бизнес-аналитик"
# 5	
# id	"25"
# name	"Гейм-дизайнер"
# 6	
# id	"165"
# name	"Дата-сайентист"
# 7	
# id	"34"
# name	"Дизайнер, художник"
# 8	
# id	"36"
# name	"Директор по информационным технологиям (CIO)"
# 9	
# id	"73"
# name	"Менеджер продукта"
# 10	
# id	"155"
# name	"Методолог"
# 11	
# id	"96"
# name	"Программист, разработчик"
# 12	
# id	"164"
# name	"Продуктовый аналитик"
# 13	
# id	"104"
# name	"Руководитель группы разработки"
# 14	
# id	"157"
# name	"Руководитель отдела аналитики"
# 15	
# id	"107"
# name	"Руководитель проектов"
# 16	
# id	"112"
# name	"Сетевой инженер"
# 17	
# id	"113"
# name	"Системный администратор"
# 18	
# id	"148"
# name	"Системный аналитик"
# 19	
# id	"114"
# name	"Системный инженер"
# 20	
# id	"116"
# name	"Специалист по информационной безопасности"
# 21	
# id	"121"
# name	"Специалист технической поддержки"
# 22	
# id	"124"
# name	"Тестировщик"
# 23	
# id	"125"
# name	"Технический директор (CTO)"
# 24	
# id	"126"
# name	"Технический писатель"
