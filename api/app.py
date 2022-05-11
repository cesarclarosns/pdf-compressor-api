from api.views import blueprints
from quart import Quart
from quart_schema import QuartSchema


def create_app(name=__name__, blueprints=None):
    app = Quart(name)
    QuartSchema(app, convert_casing=True)

    # Registrar blueprints
    if blueprints is not None:
        for bp in blueprints:
            app.register_blueprint(bp)

    return app


app = create_app(blueprints=blueprints)

if __name__ == "__main__":
    app.run()
