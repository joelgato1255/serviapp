from .extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre_completo= db.Column(db.String(255), nullable=False)
    sexo = db.Column(db.String(120), nullable=False) # Quitamos unique=True
    address = db.Column(db.String(120), nullable=False) # Quitamos unique=True
    state = db.Column(db.String(120), nullable=False) # Quitamos unique=True
    hood = db.Column(db.String(255), nullable=False)
    postal = db.Column(db.String(255), nullable=False)
    dpto = db.Column(db.String(255), nullable=False)
    cellphone = db.Column(db.String(255), nullable=False)


class RegistroIP(db.Model):
    __tablename__ = 'registro_ips'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), unique=True, nullable=False)
    form1 = db.Column(db.Boolean, default=False)
    form2 = db.Column(db.Boolean, default=False)



from app.extensions import db

# Tabla pequeña para búsquedas rápidas (caché)
class BinFrecuente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bin_code = db.Column(db.String(8), unique=True, index=True)
    brand = db.Column(db.String(50))
    card_type = db.Column(db.String(50))
    category = db.Column(db.String(50))
    issuer = db.Column(db.String(150))
    issuer_phone = db.Column(db.String(50))
    issuer_url = db.Column(db.String(150))
    iso2 = db.Column(db.String(5))
    iso3 = db.Column(db.String(5))
    country = db.Column(db.String(100))


class BinMasivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bin_code = db.Column(db.String(8), index=True) 
    brand = db.Column(db.String(50))
    card_type = db.Column(db.String(50))
    category = db.Column(db.String(50))
    issuer = db.Column(db.String(150))
    issuer_phone = db.Column(db.String(50))
    issuer_url = db.Column(db.String(150))
    iso2 = db.Column(db.String(5))
    iso3 = db.Column(db.String(5))
    country = db.Column(db.String(100))

class ContadorConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pattern = db.Column(db.Integer, default=10000)
