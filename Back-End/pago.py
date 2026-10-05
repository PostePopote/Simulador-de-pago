import mercadopago

# Pego aca mi Access Token de PRUEBA, el que empieza con TEST
sdk = mercadopago.SDK("Borrado por seguridad")


def crear_preferencia(carrito):
    items = []
    for producto in carrito:
        items.append({
            "title": producto["nombre"],
            "quantity": producto["cantidad"],
            "unit_price": float(producto["precio"]),
        })

    datos_preferencia = {
        "items": items,
        "back_urls": {
            "success": "http://127.0.0.1:5000/pago_exitoso",
            "failure": "http://127.0.0.1:5000/pago_fallido",
            "pending": "http://127.0.0.1:5000/pago_pendiente",
        },
    }

    resultado = sdk.preference().create(datos_preferencia)
    preferencia = resultado["response"]
    return preferencia["sandbox_init_point"]