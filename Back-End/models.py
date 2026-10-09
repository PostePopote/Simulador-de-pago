from flask_login import UserMixin

class Usuario(UserMixin):
    # Flask-Login exige que el usuario tenga un atributo "id"
    # Por eso agarro los datos que vienen de MySQL (un diccionario) y los acomodo aca
    def __init__(self, datos_usuario):
        self.id = datos_usuario["id"]
        self.nombre = datos_usuario["nombre"]
        self.gmail = datos_usuario["gmail"]
        self.rol = datos_usuario["rol"]