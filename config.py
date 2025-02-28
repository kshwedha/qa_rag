import os

class Config:
    """Application configuration"""
    
    # Flask settings
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    
    # Database settings
    DB_HOST = os.environ.get('HOST', 'localhost')
    DB_PORT = int(os.environ.get('PORT', 5432))
    DB_NAME = os.environ.get('NAME', 'defaultdb')
    DB_USER = os.environ.get('USER', 'postgres')
    DB_PASSWORD = os.environ.get('PASSWORD', 'postgres')
    
    # Model settings
    QA_MODEL = os.environ.get('QA_MODEL', 'deepset/roberta-base-squad2')
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')