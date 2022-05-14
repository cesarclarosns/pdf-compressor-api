from quart import Quart
from quart_schema import QuartSchema, RequestSchemaValidationError
from .views import blueprints


def create_app(name=__name__, blueprints=None):
    app = Quart(name)
    QuartSchema(app, convert_casing=True)

    # Registrar blueprints
    if blueprints is not None:
        for bp in blueprints:
            app.register_blueprint(bp)

    return app


app = create_app(blueprints=blueprints)


text_404 = "La URL solicitada no se encontró en el servidor."


@app.errorhandler(405)
def error_handling_405(error):
    return {"Error": str(error)}, 405


@app.errorhandler(500)
def error_handling_500(error):
    return {"Error": str(error)}, 500


@app.errorhandler(404)
def error_handling_404(error):
    return {"Error": str(error), "description": text_404}, 404


if __name__ == "__main__":
    app.run()
