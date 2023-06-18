from graphene import ObjectType, String, Schema
from graphene_sqlalchemy import SQLAlchemyObjectType
from .models import SpecializationModel, VacancyModel

class Specialization(SQLAlchemyObjectType):
    class Meta:
        model = SpecializationModel
        interfaces=(Node,)
        
        
class Vacancy(SQLAlchemyObjectType):
    class Meta:
        model = VacancyModel
        interfaces=(Node,)


class Query(ObjectType):#схема запросов
    specializations = graphene.List(Specialization)
    vacancies = graphene.List(Vacancy)
    
    def resolve_specializations(self, info):
        query = Specialization.get_query(info)
        return query.all()
    
    def resolve_vacancies(root, info):
        query = Vacancy.get_query(info)
        return query.all()
    

schema = Schema(query = Query)