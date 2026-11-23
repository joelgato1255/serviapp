import os

class Config:
    # Cambia esto por una clave segura en producción
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-super-secreta'
    
    # Ruta de tu base de datos (SQLite para empezar)
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'mibase.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False