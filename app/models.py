from flask_sqlalchemy import SQLAlchemy
from . import db

class SpecializationModel(db.Model):#модель для бд таблица с специализациями
    __tablename__ = 'specializations'
    sId = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = True)
    name = db.Column(db.String(255), unique = True, nullable = False)
    vacancies = db.relationship('VacancyModel', back_populates = 'specialization')
    __mapper__args__ ={
        "polymorphic_on" : vacancies
    }
    
    def __repr__(self):
        return f'Specializetion {sId} : {name}'
    
    
class VacancyModel(db.Model):#модель для бд таблица с вакансиями
    __tablename__ = 'vacancies'
    vId = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = True)
    name = db.Column(db.String(255),nullable = False)
    city = db.Column(db.String(255), nullable = True)
    minSalary = db.Column(db.Integer, nullable = True)
    maxSalary = db.Column(db.Integer, nullable = True)
    experience = db.Column(db.String(255), nullable = True)
    schedule = db.Column(db.String(255), nullable = True)
    employment = db.Column(db.String(255), nullable = True)
    description = db.Column(db.String(1000), nullable = True)
    keySkills = db.Column(db.String(255), nullable = True)
    employer = db.Column(db.String(255), nullable = True)
    publishedAt = db.Column(db.DateTime(), nullable = True)
    specializationId = db.Column(db.Integer(), db.ForeignKey('specializations.sId'), nullable = False)
    specialization = db.relationship('SpecializationModel', back_populates = 'vacancies')
    __mapper__args__ ={
        "polymorphic_on" : specialization
    }
    
    def __repr__(self):
        return f"Vacancy {vId} : {name}" 