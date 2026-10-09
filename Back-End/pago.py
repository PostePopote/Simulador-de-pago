import mercadopago

# Conecto el SDK de Mercado Pago con mi Access Token de PRUEBA 
sdk = mercadopago.SDK("borra todo esto menos las "" y pega el access token")

def crear_preferencia(carrito):
    # Una preferencia es el "pedido" que le mando a Mercado Pago para que lo cobre
    # Armo un item por cada producto del carrito, con su nombre, cantidad y precio
    items = []
    for producto in carrito:
        items.append({
            "title": producto["nombre"],
            "quantity": producto["cantidad"],
            "unit_price": float(producto["precio"]),
        })
    # Las back_urls son a donde Mercado Pago redirige al usuario
    # dependiendo de como termino el pago
    datos_preferencia = {
        "items": items,
        "back_urls": {
            "success": "http://127.0.0.1:5000/pago_exitoso",
            "failure": "http://127.0.0.1:5000/pago_fallido",
            "pending": "http://127.0.0.1:5000/pago_pendiente",
        },
    }
    # Le mando los datos a Mercado Pago y me devuelve la preferencia ya creada
    resultado = sdk.preference().create(datos_preferencia)
    preferencia = resultado["response"]
    # sandbox_init_point es el link al checkout de PRUEBA, sin mover dinero real
    # (si uso una credencial TEST-, este es el link que tengo que usar)
    return preferencia["sandbox_init_point"]