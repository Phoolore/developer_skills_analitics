from flask_sqlalchemy import SQLAlchemy
from . import db

class Specialization(db.Model):
    id = db.Column(db.Integer, primaru_key = True)
    name = db.Column(db.String(255), unique = True, nullable = False)
    vacancies = db.Column('Vacancy', back_populates = 'Specialization')
    
    def __repr__(self):
        return f'Specializetion {id} : {name}'
    
    
class Vacancy(db.Model):
    id = db.Column(db.Integer, primaru_key = True)
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
    specialization_id = db.Column(db.Integer(), db.ForeignKey('Specialization.id', nullable = False))
    specialization = db.relationship('Specialization', back_populates = 'Vacancy')
    
    def __repr__(self):
        return f"Vacancy {id} : {name}" 