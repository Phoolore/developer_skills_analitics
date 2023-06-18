from flask_sqlalchemy import SQLAlchemy
from . import db

class SpecializationModel(db.Model):#модель для бд таблица с специализациями
    __tablename__ = 'specializations'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), unique = True, nullable = False)
    vacancies = db.relationship('vacancies', back_populates = 'specialization')
    __mapper__args__ ={
        "polymorphic_on" : vacancies
    }
    
    def __repr__(self):
        return f'Specializetion {id} : {name}'
    
    
class VacancyModel(db.Model):#модель для бд таблица с вакансиями
    __tablename__ = 'vacancies'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), unique = True, nullable = False)
    city = db.Column(db.String(255), nullable = True)
    min_salary = db.Column(db.Integer, nullable = True)
    max_salary = db.Column(db.Integer, nullable = True)
    experience = db.Column(db.String(255), nullable = True)
    schedule = db.Column(db.String(255), nullable = True)
    employment = db.Column(db.String(255), nullable = True)
    description = db.Column(db.String(1000), nullable = True)
    key_skills = db.Column(db.String(255), nullable = True)
    employer = db.Column(db.String(255), nullable = True)
    published_at = db.Column(db.DateTime(), nullable = True)
    specialization_id = db.Column(db.Integer(), db.ForeignKey('specializations.id'))
    specialization = db.relationship('specializations', back_populates = 'vacancies')
    __mapper__args__ ={
        "polymorphic_on" : specialization
    }
    
    def __repr__(self):
        return f"Vacancy {id} : {name}" 