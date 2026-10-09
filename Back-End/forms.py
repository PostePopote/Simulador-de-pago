from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# Formulario de registro, FlaskForm se encarga de la proteccion CSRF automaticamente
class RegistroForm(FlaskForm):
    # DataRequired hace que el campo no se pueda dejar vacio
    nombre = StringField("Nombre", validators=[DataRequired()])
    # Email valida que tenga formato de correo (necesita la libreria email_validator instalada)
    gmail = StringField("Gmail", validators=[DataRequired(), Email()])
    # Length pone un minimo de caracteres para la contraseña
    contraseña = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    # EqualTo compara este campo con el campo "contraseña" de arriba
    # Si no coinciden, muestra el mensaje de error
    confirmar = PasswordField(
        "Confirmar contraseña",
        validators=[DataRequired(), EqualTo("contraseña", message="Las contraseñas no coinciden")]
    )
    # El boton que envia el formulario
    enviar = SubmitField("Registrarme")