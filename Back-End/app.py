from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import obtener_productos, obtener_producto_por_id, insertar_producto, actualizar_producto
from pago import crear_preferencia

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
        usuario = request.form["usuario"]
        password = request.form["password"]
        # Usuario de prueba sin conexion a la base de datos.
        if usuario == "admin" and password == "1234":
            session["usuario"] = usuario
            session["rol"] = "admin"
            flash("Sesion iniciada correctamente", "exito")
            return redirect(url_for("home"))
        else:
            flash("Usuario o contraseña incorrectos", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesion cerrada", "exito")
    return redirect(url_for("home"))

@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]
        tipo = request.form["tipo"]
        categoria = request.form["categoria"]
        imagen = request.form["imagen"]
        descripcion = request.form["descripcion"]
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
        imagen = request.form["imagen"]
        descripcion = request.form["descripcion"]
        actualizar_producto(id_producto, nombre, precio, stock, tipo, categoria, imagen, descripcion)
        flash("Producto actualizado correctamente", "exito")
        return redirect(url_for("productos"))
    producto = obtener_producto_por_id(id_producto)
    return render_template("editar.html", producto=producto)

# Todo esto es del carro
@app.route("/carrito")
def carrito():
    lista_carrito = session.get("carrito", [])
    # Multiplico precio por cantidad en cada producto, y sumo todo
    total = sum(item["precio"] * item["cantidad"] for item in lista_carrito)
    return render_template("carrito.html", carrito=lista_carrito, total=total)

# Agrego el producto al carrito, o le sumo 1 a la cantidad si ya estaba
@app.route("/carrito/agregar/<int:id_producto>", methods=["POST"])
def agregar_al_carrito(id_producto):
    carrito = session.get("carrito", [])
    # Busco si el producto ya esta en el carrito
    ya_esta = False
    for item in carrito:
        if item["id"] == id_producto:
            item["cantidad"] = item["cantidad"] + 1
            ya_esta = True
            break
    # Si no estaba, lo agrego nuevo con cantidad 1
    if not ya_esta:
        producto = obtener_producto_por_id(id_producto)
        producto["precio"] = float(producto["precio"])
        producto["cantidad"] = 1
        carrito.append(producto)
    session["carrito"] = carrito
    flash("Producto agregado al carrito", "exito")
    return redirect(url_for("productos"))


# Le resto 1 a la cantidad, y si llega a 0 lo saco del carrito
@app.route("/carrito/quitar/<int:id_producto>", methods=["POST"])
def quitar_del_carrito(id_producto):
    carrito = session.get("carrito", [])
    nuevo_carrito = []
    for item in carrito:
        if item["id"] == id_producto:
            item["cantidad"] = item["cantidad"] - 1
            if item["cantidad"] > 0:
                nuevo_carrito.append(item)
            # Si la cantidad llega a 0, no lo agrego de vuelta (queda eliminado)
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

    #Toma todos los productos
    link_pago = crear_preferencia(carrito)
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

# Le da la chispa de inicio para que arranque la app
if __name__ == "__main__":
    app.run(debug=True)