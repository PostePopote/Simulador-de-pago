import mysql.connector

def obtener_conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Loforte_2008",
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