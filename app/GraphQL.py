import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .models import SpecializationModel, VacancyModel
from . import db


#объект специализаций для схемы запросов
class Specialization(SQLAlchemyObjectType):
    """Объект специализаций для схемы запрос"""
    class Meta:
        model = SpecializationModel
        interfaces=(graphene.relay.Node,)
        
#объект вакансий для схемы запросов        
class Vacancy(SQLAlchemyObjectType):
    """Объект вакансий для схемы запросов"""
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


#объект добавления специализаций для схемы мутаций
class AddSpecializationMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=False)
        name = graphene.String(required=True)
        
    status = graphene.Boolean()

    def mutate(self, info, name, id = None):
        spec = SpecializationModel(id = id, name = name)
        db.session.add(spec)
        db.session.commit()
        status = True
        return AddSpecializationMutation(status = status)

class AddVacancyMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=False)
        name = graphene.String(required=True)
        city = graphene.String(required=False)
        minSalary = graphene.Int(required=False)
        maxSalary = graphene.Int(required=False)
        experience = graphene.String(required=False)
        schedule = graphene.String(required=False)
        employment = graphene.String(required=False)
        description = graphene.String(required=False)
        keySkills = graphene.String(required=False)
        employer = graphene.String(required=False)
        publishedAt = graphene.Date(required=False)
        specializationId = graphene.Int(required=True)
    
    status = graphene.Boolean()
    
    def mutate(self, info, name, specializationId, id = None, city = None, minSalary = None, maxSalary = None, experience = None, schedule = None, employment = None, description = None, keySkills = None, employer = None, publishedAt = None):
        vac = VacancyModel(id = id, name = name, city = city, minSalary = minSalary, maxSalary = maxSalary, experience = experience, schedule = schedule, employment = employment, description = description, keySkills = keySkills, employer = employer, publishedAt = publishedAt, specializationId = specializationId)
        db.session.add(vac)
        db.session.commit()
        status = True
        return AddVacancyMutation(status = status)


#схема мутаций
class Mutation(graphene.ObjectType):
    saveSpecialization = AddSpecializationMutation.Field()
    saveVacancy = AddVacancyMutation.Field()
    
#конечная схема     
schema = graphene.Schema(query = Query, mutation = Mutation)