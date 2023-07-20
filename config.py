import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_ENGINE_ID = os.getenv('GOOGLE_ENGINE_ID')