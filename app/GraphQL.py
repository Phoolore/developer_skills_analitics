import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .models import SpecializationModel, VacancyModel
from . import db

#объект специализаций для схемы запросов
class Specialization(SQLAlchemyObjectType):
    class Meta:
        model = SpecializationModel
        interfaces=(graphene.relay.Node,)
        
#объект вакансий для схемы запросов        
class Vacancy(SQLAlchemyObjectType):
    class Meta:
        model = VacancyModel
        interfaces=(graphene.relay.Node,)


#схема запросов
class Query(graphene.ObjectType):
    node = graphene.Node.Field()
    Getspecializations = SQLAlchemyConnectionField(Specialization.connection)
    Getvacancies = SQLAlchemyConnectionField(Vacancy.connection)
    
    def resolve_specializations(self, info):
        query = Specialization.get_query(info)
        return query.all()
    
    def resolve_vacancies(root, info):
        query = Vacancy.get_query(info)
        return query.all()
    
    
#схема запросов
schema_query = graphene.Schema(query = Query)


#объект добавления специализаций для схемы мутаций
class AddSpecialization(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        
    spec = graphene.Field(lambda: Specialization)

    def mutate(self, info, id, name):
        spec = SpecializationModel(id = id, name = name)
        db.session.add(spec)
        db.session.commit()
        return AddSpecialization(spec = spec)

class AddVacancy(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        city = graphene.String(required=True)
        min_salary = graphene.Int(required=True)
        max_salary = graphene.Int(required=True)
        experience = graphene.String(required=True)
        schedule = graphene.String(required=True)
        employment = graphene.String(required=True)
        description = graphene.String(required=True)
        key_skills = graphene.String(required=True)
        employer = graphene.String(required=True)
        published_at = graphene.Date(required=True)
        specialization_id = graphene.Int(required=True)
    
    vac = graphene.Field(lambda: Vacancy)
    
    def mutate(self, info, id, name, city, min_salary, max_salary, experience, schedule, employment, description, key_skills, employer, published_at, specialization_id):
        vac = VacancyModel(id = id, name = name, city = city, min_salary = min_salary, max_salary = max_salary, experience = experience, schedule = schedule, employment = employment, description = description, key_skills = key_skills, employer = employer, published_at = published_at, specialization_id = specialization_id)
        db.session.add(vac)
        db.session.commit()
        return AddVacancy(vac = vac)


#схема мутаций
class Mutation(graphene.ObjectType):
    save_specialization = AddSpecialization.Field()
    save_vacancy = AddVacancy.Field()
    
#схема мутаций    
schema_mutation = graphene.Schema(query = Query, mutation = Mutation)