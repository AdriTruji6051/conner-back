from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                    static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    app.config['JWT_SECRET_KEY'] = '0191ee57-49ca-1994-0cd6-1f77b76b7667'
    

    # Configurar la duración del token de acceso
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=18)  # Token durará 12 horas


    #Manejo de tokens
    jwt = JWTManager(app)
    
    # Registro de rutas
    from app.routes import routes
    app.register_blueprint(routes)

    return app