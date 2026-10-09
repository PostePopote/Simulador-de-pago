from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Esta instancia se comparte entre app.py y este archivo
db = SQLAlchemy()
class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    gmail = db.Column(db.String(255))
    contraseña = db.Column(db.String(255))
    rol = db.Column(db.String(255))
    # Flask-Login busca un atributo "id" por defecto, pero mi columna se llama id_usuario
    # Con esta property, cuando alguien escriba usuario.id, le devuelvo id_usuario
    @property
    def id(self):
        return self.id_usuario

class Producto(db.Model):
    __tablename__ = "productos"
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    precio = db.Column(db.Numeric)
    stock = db.Column(db.Integer)
    tipo = db.Column(db.String(255))
    categoria = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    # Mismo truco: tus templates usan p.id, y la columna real es id_producto
    @property
    def id(self):
        return self.id_producto