import os
from dotenv import load_dotenv

load_dotenv()

# Абсолютный путь к папке проекта (самое надёжное решение)
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-change-in-production')
    
    # Путь к базе данных — теперь точно будет работать
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "..", "instance", "database.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.join(basedir, "..", "uploads")
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}
