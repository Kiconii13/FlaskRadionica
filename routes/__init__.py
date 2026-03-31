from .web import web_bp


def register_routes(app):
    # Registruje blueprint-ove za rute
    app.register_blueprint(web_bp)
