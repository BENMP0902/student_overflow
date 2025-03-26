#rA2_93#7tK2Meaj
#cvVElgt1FXxAIgLKrm0y07oWcO1L76
# Flask es la librería que nos ayudará a crear un servidor para nuestra API
from flask import Flask
# Importamos la función que se encarga de cargar las rutas
from routes import cargar_rutas

from extensions import db_s, jwt

# flask: Librería
# Flask: módulo (clase)

# Vamos a crear un objeto que contendrá los métodos necesarios para nuestro servidor
app = Flask(__name__)

#1. Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.atgxanqwsnttopfxzlwm:rA2_93#7tK2Meaj@aws-0-us-west-1.pooler.supabase.com:6543/postgres'


#2. Desactivar el track modification
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#3. Firma para los tokens
app.config['JWT_SECRET_KEY'] = 'cvVElgt1FXxAIgLKrm0y07oWcO1L76'  

#Agregamos 3 configuraciones para que app maneje las cookies
#El acceso estara en las cookies
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'


#Proteccion contra ataques desactivada
app.config['JWT_COOKIE_CSRF_PROTECCION'] = False


db_s.init_app(app)

#Establece conexion entre jwt y la app
jwt.init_app(app)

#Cargamos las rutas desde el archivo routes.py
cargar_rutas(app)

app.run(port=8000, debug=True)