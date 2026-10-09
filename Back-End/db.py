import mysql.connector

def obtener_conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Cambiar Contraseña",
        database="SakuraShop"
    )
    return conexion

def obtener_productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    # Uso "AS id" para que en Python siga llegando como p.id
    cursor.execute(
        """SELECT id_producto AS id, nombre, precio, stock, tipo, categoria, descripcion, imagen
        FROM productos"""
    )
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return productos

def obtener_producto_por_id(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """SELECT id_producto AS id, nombre, precio, stock, tipo, categoria, descripcion, imagen
        FROM productos WHERE id_producto = %s""",
        (id_producto,)
    )
    producto = cursor.fetchone()
    cursor.close()
    conexion.close()
    return producto

def insertar_producto(nombre, precio, stock, tipo, categoria, imagen, descripcion):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """INSERT INTO productos (nombre, precio, stock, tipo, categoria, imagen, descripcion)
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (nombre, precio, stock, tipo, categoria, imagen, descripcion)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

def actualizar_producto(id_producto, nombre, precio, stock, tipo, categoria, imagen, descripcion):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """UPDATE productos
        SET nombre = %s, precio = %s, stock = %s, tipo = %s, categoria = %s, imagen = %s, descripcion = %s
        WHERE id_producto = %s""",
        (nombre, precio, stock, tipo, categoria, imagen, descripcion, id_producto)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

def obtener_usuario_por_gmail(gmail):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_usuario AS id, nombre, gmail, contraseña, rol FROM usuarios WHERE gmail = %s",
        (gmail,)
    )
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return usuario

def obtener_usuario_por_id(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_usuario AS id, nombre, gmail, contraseña, rol FROM usuarios WHERE id_usuario = %s",
        (id_usuario,)
    )
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return usuario

def insertar_usuario(nombre, gmail, contraseña_hasheada):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    # El rol por defecto es "usuario", el admin lo cambias a mano en la base si hace falta
    cursor.execute(
        "INSERT INTO usuarios (nombre, gmail, contraseña, rol) VALUES (%s, %s, %s, %s)",
        (nombre, gmail, contraseña_hasheada, "usuario")
    )
    conexion.commit()
    cursor.close()
    conexion.close()