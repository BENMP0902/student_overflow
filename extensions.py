#Este archivo evitara las importaciones circulares

from flask_sqlalchemy import SQLAlchemy


#JWT es una clase que a traves de atributos y de metodos
#controla los procesos para generar JWT y utilizxarlos
from flask_jwt_extended import JWTManager

 #Creamos un objeto de tipo SQLAlquemy que va a controlar toda la base de datos
db_s = SQLAlchemy()



#Creamos un objeto JWT
jwt = JWTManager()