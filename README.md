SakuraShop es una tienda online de musica general y productos originarios de japon. 
Posee una estetica inspirada en el sakura que es el cerezo japones,
el monte fuji, el torii que son entradas a templos y el kintsugi que es el arte de reparar
ceramica con oro, osea no ocultar las fisuras y uniones.

Que use para este hermoso proyecto?
Python + Flask para el framework web
Flask-Alchemy para la conexion y manejo de la base de datos
Flask-Login para manejar todo el asunto de sesiones de usuarios
Flask-WTF para los registros y validaciones
MySql para hacer la base de datos
Jinja2 para las plantillas del html
Mercado Pago SDK para el asunto de pagos y cobros
Werkzeug para encriptar contraseñas y verificar contraselas (`generate_password_hash` / `check_password_hash`)

Funcionalidades:
- Catálogo de productos con categorías (Música, Japón, Manga, Cómic, Figura, CD, Blu-Ray)
- Registro e inicio de sesión de usuarios, con roles usuario y admin
- Panel de administrador: agregar y editar productos, con subida de imágenes
- Carrito de compras por usuario (guardado en sesión), con suma y resta de cantidades
- Pago integrado con Mercado Pago (modo sandbox / pruebas)
- Mensajes de confirmación y error (flash messages) en toda la app


Como instalar
Paso 1: clonamos el repositorio
git clone https://github.com/PostePopote/Simulador-de-pago.git
cd Simulador-de-pago

Paso 2: Hacemos un entorno virtual
python -m venv **insertar nombre**

Paso 3: Instalamos las dependencias
pip install -r requirements.txt

Paso 4: Creamos la base de datos
Con MySQL encendido, importá el archivo `SakuraShop.sql` desde MySQL Workbench o phpMyAdmin. Esto crea la base `SakuraShop` con todas sus tablas (usuarios, productos, carrito, pedidos, pagos, etc).

Paso 5: Configura la conexión a la base de datos
Vas a db.py y alli encontraras la siguiente estructura al inicio

def obtener_conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="cambia contraseña",
        database="SakuraShop"
    )
    return conexion

En password donde dice cambia contraseña debes poner la contraseña tuya de sql

Paso 6: Configura el Mercado Pago
En `Back-End/pago.py`, pegá tu **Access Token de prueba** (el que empieza con `TEST-`), obtenido desde el Panel del Desarrollador de Mercado Pago:
sdk = mercadopago.SDK("Borrado por seguridad")

Paso 7: Ejecutamos la aplicación
cd Back-End
python app.py

Abre en el navegador: `http://127.0.0.1:5000`

Notas

- El proyecto corre en modo desarrollo (`debug=True`), no está pensado para producción.
- Las credenciales de Mercado Pago usadas son de **prueba** (sandbox), no se procesan pagos reales.
- Las contraseñas de los usuarios se guardan encriptadas (hash), nunca en texto plano.