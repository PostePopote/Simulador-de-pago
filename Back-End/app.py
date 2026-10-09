import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import obtener_productos, obtener_producto_por_id, insertar_producto, actualizar_producto, obtener_usuario_por_gmail, insertar_usuario
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

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/productos")
def productos():
    # Ahora los productos vienen de MySQL
    lista_productos = obtener_productos()
    return render_template("productos.html", productos=lista_productos)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        gmail = request.form["usuario"]
        password = request.form["password"]
        # Busco el usuario en la base por su gmail
        usuario = obtener_usuario_por_gmail(gmail)
        # El "usuario and" es importante: si el gmail no existe, usuario es None,
        # y Python corta ahi sin llegar a check_password_hash (si no, tiraria error)
        # check_password_hash encripta el password escrito y lo compara con el hash guardado
        # (la contraseña real nunca se puede "desencriptar", solo se compara asi)
        if usuario and check_password_hash(usuario["contraseña"], password):
            session["usuario"] = usuario["nombre"]
            session["rol"] = usuario["rol"]
            flash("Sesion iniciada correctamente", "exito")
            return redirect(url_for("home"))
        else:
            flash("Usuario o contraseña incorrectos", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    # session.clear() borra todo lo guardado: usuario, rol y tambien el carrito
    session.clear()
    flash("Sesion cerrada", "exito")
    return redirect(url_for("home"))

# Ruta absoluta a static/assets, construida a partir de donde esta este archivo (app.py)
CARPETA_IMAGENES = os.path.join(app.root_path, "..", "Front-End", "static", "assets")
# Por si la carpeta no existe todavia, la creo
os.makedirs(CARPETA_IMAGENES, exist_ok=True)

@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]
        tipo = request.form["tipo"]
        categoria = request.form["categoria"]
        descripcion = request.form["descripcion"]
        # El archivo subido viene de request.files, no de request.form
        archivo_imagen = request.files["imagen"]
        # secure_filename limpia el nombre del archivo, por si tiene espacios o caracteres raros
        nombre_archivo = secure_filename(archivo_imagen.filename)
        # Lo guardo fisicamente en static/assets
        ruta_guardado = os.path.join(CARPETA_IMAGENES, nombre_archivo)
        archivo_imagen.save(ruta_guardado)
        # En la base solo guardo la ruta relativa, como ya veniamos haciendo
        imagen = f"assets/{nombre_archivo}"
        insertar_producto(nombre, precio, stock, tipo, categoria, imagen, descripcion)
        flash("Producto agregado correctamente", "exito")
        return redirect(url_for("productos"))

    return render_template("agregar.html")

# Edito unicamente aquel producto seleccionado por su id
@app.route("/editar/<int:id_producto>", methods=["GET", "POST"])
def editar(id_producto):
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]
        tipo = request.form["tipo"]
        categoria = request.form["categoria"]
        descripcion = request.form["descripcion"]
        # Traigo el producto actual para saber que imagen tenia, por si no suben una nueva
        producto_actual = obtener_producto_por_id(id_producto)
        imagen = producto_actual["imagen"]
        # Si el input de archivo viene con algo cargado, piso la imagen vieja
        archivo_imagen = request.files["imagen"]
        if archivo_imagen.filename != "":
            nombre_archivo = secure_filename(archivo_imagen.filename)
            ruta_guardado = os.path.join(CARPETA_IMAGENES, nombre_archivo)
            archivo_imagen.save(ruta_guardado)
            imagen = f"assets/{nombre_archivo}"
        actualizar_producto(id_producto, nombre, precio, stock, tipo, categoria, imagen, descripcion)
        flash("Producto actualizado correctamente", "exito")
        return redirect(url_for("productos"))
    producto = obtener_producto_por_id(id_producto)
    return render_template("editar.html", producto=producto)

# Todo esto es del carro
@app.route("/carrito")
def carrito():
    # session.get("carrito", []) trae el carrito guardado, o una lista vacia si no hay nada todavia
    lista_carrito = session.get("carrito", [])
    # Multiplico precio por cantidad en cada producto, y sumo todo
    total = sum(item["precio"] * item["cantidad"] for item in lista_carrito)
    return render_template("carrito.html", carrito=lista_carrito, total=total)

# Agrego el producto al carrito, o le sumo 1 a la cantidad si ya estaba
@app.route("/carrito/agregar/<int:id_producto>", methods=["POST"])
def agregar_al_carrito(id_producto):
    carrito = session.get("carrito", [])
    # Recorro el carrito a ver si el producto ya esta cargado
    ya_esta = False
    for item in carrito:
        if item["id"] == id_producto:
            item["cantidad"] = item["cantidad"] + 1
            ya_esta = True
            break  # Ya lo encontre, no hace falta seguir recorriendo
    # Si no estaba en el carrito, lo busco en la base y lo agrego como nuevo con cantidad 1
    if not ya_esta:
        producto = obtener_producto_por_id(id_producto)
        # Convierto el precio a float porque el Decimal de MySQL no se guarda bien en la sesion
        producto["precio"] = float(producto["precio"])
        producto["cantidad"] = 1
        carrito.append(producto)
    # Piso el carrito viejo de la sesion con el actualizado
    session["carrito"] = carrito
    flash("Producto agregado al carrito", "exito")
    return redirect(url_for("productos"))


# Le resto 1 a la cantidad, y si llega a 0 lo saco del carrito
@app.route("/carrito/quitar/<int:id_producto>", methods=["POST"])
def quitar_del_carrito(id_producto):
    carrito = session.get("carrito", [])
    # Armo un carrito nuevo en vez de modificar el viejo mientras lo recorro
    nuevo_carrito = []
    for item in carrito:
        if item["id"] == id_producto:
            item["cantidad"] = item["cantidad"] - 1
            if item["cantidad"] > 0:
                nuevo_carrito.append(item)
            # Si la cantidad llega a 0, no lo agrego de vuelta (queda eliminado)
        else:
            # Es otro producto, lo dejo como estaba
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
    # crear_preferencia le manda el carrito a Mercado Pago y devuelve el link del checkout
    link_pago = crear_preferencia(carrito)
    # redirect manda al usuario afuera de mi pagina, directo al checkout de Mercado Pago
    return redirect(link_pago)

@app.route("/pago_exitoso")
def pago_exitoso():
    # Vacio el carrito porque la compra ya se completo
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
    # FlaskForm necesita crear una instancia del formulario para validarlo y mostrarlo
    form = RegistroForm()
    # validate_on_submit() revisa dos cosas a la vez: que sea un POST,
    # y que todos los validadores del formulario (DataRequired, Email, etc) pasen
    if form.validate_on_submit():
        nombre = form.nombre.data
        gmail = form.gmail.data
        contraseña = form.contraseña.data
        # Me fijo que no exista ya un usuario con ese gmail
        usuario_existente = obtener_usuario_por_gmail(gmail)
        if usuario_existente:
            flash("Ya existe una cuenta con ese gmail", "error")
            return redirect(url_for("register"))
        # Encripto la contraseña antes de guardarla, nunca en texto plano
        contraseña_hasheada = generate_password_hash(contraseña)
        insertar_usuario(nombre, gmail, contraseña_hasheada)
        flash("Cuenta creada correctamente, ya podes iniciar sesion", "exito")
        return redirect(url_for("login"))
    # Si no se envio el formulario, o si algun campo no paso la validacion,
    # vuelvo a mostrar register.html (con los errores marcados si los hay)
    return render_template("register.html", form=form)

# Le da la chispa de inicio para que arranque la app
if __name__ == "__main__":
    app.run(debug=True)