from .GraphQL import schema
from . import app

with app.app_context():
    # Загрузка специализаций
    for i in range(1000):
        query = 'mutation{ saveSpecialization(name:"' + str(i) + '"){ status }}'
        data = schema.execute(query)
        with open("data.txt", "w+") as f:
                f.write(str(data))
    # Загрузка вакансий
    with open("test05.csv", "r", encoding = "utf-8-sig") as f:  
        for i in f.readlines():
            pack = i.split(";")
            print(pack)
            skills = []
            for i in pack[9].split(','):
                skills += f"'{i}'"
            query = '''mutation{ saveVacancy(vId : "''' + pack[0] + '''",name:"''' + pack[1] + '''", city: "''' + pack[2] + '''",minSalary: ''' + pack[3] + ''', maxSalary: ''' + pack[4] + ''', experience : "''' + pack[5] + '''", shedule : "''' + pack[6] + '''", employment: "''' + pack[7] + '''",description:"''' + pack[8] + '''",keySkills: "[''' + str(skills) + ''']",employer: "''' + pack[10] + '''",  publishedAt : "''' + pack[11] + '''",specializationId: ''' + pack[12] + '''){ status } }'''
            data = schema.execute(query)
            with open("data.txt", "a+",encoding = "utf-8-sig" ) as f:
                f.write(str(data))