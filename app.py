from flask import Flask


from routes.admin_routes import admin_bp
from routes.inicio_routes import inicio_bp
from routes.articulo_routes import articulo_bp
from routes.cajas_routes import cajas_bp
from routes.ubicaciones_routes import ubicaciones_bp




app = Flask(__name__)


app.register_blueprint(inicio_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(articulo_bp)
app.register_blueprint(cajas_bp)
app.register_blueprint(ubicaciones_bp)


if __name__ == "__main__":
    app.run()
