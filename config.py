import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database/pptgen.db'
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or f"sqlite:///{os.path.join(BASE_DIR, 'database', 'pptgen.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'storage/ppts'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 16 * 1024 * 1024)  # 16MB max file size
    
    # PPT Generation Settings
    TEMPLATE_FOLDER = 'templates/ppt'
    ORGANIZATION_LOGO = 'static/images/org_logo.png'
    DEFAULT_THEME = 'corporate'
    
    # Application Settings
    PRESENTATIONS_PER_PAGE = 10
    MAX_VERSIONS_DISPLAY = 5