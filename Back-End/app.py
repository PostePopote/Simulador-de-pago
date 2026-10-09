import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Usuario, Producto
from pago import crear_preferencia
from forms import RegistroForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Le indico a Flask donde estan los templates y static porque si no el tonoto se pierde
app = Flask(
    __name__,
    template_folder="../Front-End/templates",
    static_folder="../Front-End/static",
)
app.secret_key = "contraseña_secreta_SakuraShop"
# Le digo a SQLAlchemy a que base de datos conectarse
# Cambia "CONTRASEÑA" por tu contraseña real de MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:CONTRASEÑA@localhost/SakuraShop"
# Conecto SQLAlchemy con mi app
db.init_app(app)

# Configuro Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Tenes que iniciar sesion para acceder a esa pagina"
login_manager.login_message_category = "error"

@login_manager.user_loader
def cargar_usuario(id_usuario):
    # Query.get busca por clave primaria directo, sin escribir SQL
    return Usuario.query.get(int(id_usuario))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/productos")
def productos():
    # Query.all() trae todos los productos, como objetos Producto
    lista_productos = Producto.query.all()
    return render_template("productos.html", productos=lista_productos)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        gmail = request.form["usuario"]
        password = request.form["password"]
        # filter_by busca donde gmail sea igual al que escribio el usuario
        usuario = Usuario.query.filter_by(gmail=gmail).first()
        if usuario and check_password_hash(usuario.contraseña, password):
            login_user(usuario)
            flash("Sesion iniciada correctamente", "exito")
            return redirect(url_for("home"))
        else:
            flash("Usuario o contraseña incorrectos", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    flash("Sesion cerrada", "exito")
    return redirect(url_for("home"))

# Ruta absoluta a static/assets, construida a partir de donde esta este archivo (app.py)
CARPETA_IMAGENES = os.path.join(app.root_path, "..", "Front-End", "static", "assets")
os.makedirs(CARPETA_IMAGENES, exist_ok=True)

@app.route("/agregar", methods=["GET", "POST"])
@login_required
def agregar():
    if request.method == "POST":
        archivo_imagen = request.files["imagen"]
        nombre_archivo = secure_filename(archivo_imagen.filename)
        ruta_guardado = os.path.join(CARPETA_IMAGENES, nombre_archivo)
        archivo_imagen.save(ruta_guardado)
        # Armo el objeto Producto con los datos del formulario
        nuevo_producto = Producto(
            nombre=request.form["nombre"],
            precio=request.form["precio"],
            stock=request.form["stock"],
            tipo=request.form["tipo"],
            categoria=request.form["categoria"],
            imagen=f"assets/{nombre_archivo}",
            descripcion=request.form["descripcion"],
        )
        # Lo agrego a la sesion de SQLAlchemy y confirmo con commit, como el commit() de antes
        db.session.add(nuevo_producto)
        db.session.commit()
        flash("Producto agregado correctamente", "exito")
        return redirect(url_for("productos"))
    return render_template("agregar.html")

@app.route("/editar/<int:id_producto>", methods=["GET", "POST"])
@login_required
def editar(id_producto):
    producto = Producto.query.get(id_producto)
    if request.method == "POST":
        producto.nombre = request.form["nombre"]
        producto.precio = request.form["precio"]
        producto.stock = request.form["stock"]
        producto.tipo = request.form["tipo"]
        producto.categoria = request.form["categoria"]
        producto.descripcion = request.form["descripcion"]
        archivo_imagen = request.files["imagen"]
        if archivo_imagen.filename != "":
            nombre_archivo = secure_filename(archivo_imagen.filename)
            ruta_guardado = os.path.join(CARPETA_IMAGENES, nombre_archivo)
            archivo_imagen.save(ruta_guardado)
            producto.imagen = f"assets/{nombre_archivo}"
        # No hace falta "actualizar" nada: como el objeto ya viene de la base,
        # SQLAlchemy nota los cambios solo y los guarda con este commit
        db.session.commit()
        flash("Producto actualizado correctamente", "exito")
        return redirect(url_for("productos"))
    return render_template("editar.html", producto=producto)

# Todo esto es del carro
@app.route("/carrito")
def carrito():
    lista_carrito = session.get("carrito", [])
    total = sum(item["precio"] * item["cantidad"] for item in lista_carrito)
    return render_template("carrito.html", carrito=lista_carrito, total=total)

@app.route("/carrito/agregar/<int:id_producto>", methods=["POST"])
def agregar_al_carrito(id_producto):
    carrito = session.get("carrito", [])
    ya_esta = False
    for item in carrito:
        if item["id"] == id_producto:
            item["cantidad"] = item["cantidad"] + 1
            ya_esta = True
            break
    if not ya_esta:
        producto = Producto.query.get(id_producto)
        # La session de Flask guarda la cookie como JSON, y un objeto Producto no se puede
        # convertir a JSON directo, por eso armo un diccionario a mano con lo que necesito
        producto_para_carrito = {
            "id": producto.id,
            "nombre": producto.nombre,
            "precio": float(producto.precio),
            "imagen": producto.imagen,
            "categoria": producto.categoria,
            "cantidad": 1,
        }
        carrito.append(producto_para_carrito)
    session["carrito"] = carrito
    flash("Producto agregado al carrito", "exito")
    return redirect(url_for("productos"))

@app.route("/carrito/quitar/<int:id_producto>", methods=["POST"])
def quitar_del_carrito(id_producto):
    carrito = session.get("carrito", [])
    nuevo_carrito = []
    for item in carrito:
        if item["id"] == id_producto:
            item["cantidad"] = item["cantidad"] - 1
            if item["cantidad"] > 0:
                nuevo_carrito.append(item)
        else:
            nuevo_carrito.append(item)
    session["carrito"] = nuevo_carrito
    flash("Producto quitado del carrito", "exito")
    return redirect(url_for("carrito"))

# Todo esto es del Mercado Pago
@app.route("/pagar", methods=["POST"])
def pagar():
    carrito = session.get("carrito", [])
    if not carrito:
        flash("Tu carrito esta vacio", "error")
        return redirect(url_for("carrito"))
    link_pago = crear_preferencia(carrito)
    return redirect(link_pago)

@app.route("/pago_exitoso")
def pago_exitoso():
    session["carrito"] = []
    flash("Pago realizado correctamente", "exito")
    return redirect(url_for("carrito"))

@app.route("/pago_fallido")
def pago_fallido():
    flash("El pago fallo", "error")
    return redirect(url_for("carrito"))

@app.route("/pago_pendiente")
def pago_pendiente():
    flash("El pago esta pendiente", "exito")
    return redirect(url_for("carrito"))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistroForm()
    if form.validate_on_submit():
        usuario_existente = Usuario.query.filter_by(gmail=form.gmail.data).first()
        if usuario_existente:
            flash("Ya existe una cuenta con ese gmail", "error")
            return redirect(url_for("register"))
        nuevo_usuario = Usuario(
            nombre=form.nombre.data,
            gmail=form.gmail.data,
            contraseña=generate_password_hash(form.contraseña.data),
            rol="usuario",
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Cuenta creada correctamente, ya podes iniciar sesion", "exito")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)