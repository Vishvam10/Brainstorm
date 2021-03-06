import os

from flask import Flask
from flask_restful import Api
from application.api import CardAPI, DeckAPI, ReviewAPI
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_cors import CORS
from waitress import serve


if __name__ == "__main__":
    my_app = None
    api = None

    my_app = Flask(__name__, template_folder="templates")
    my_app.config.from_object(LocalDevelopmentConfig)
    db.init_app(my_app)
    api = Api(my_app)
    CORS(my_app)
    my_app.app_context().push()

    from application.controllers import *
    from application.api import UserAPI
    api.add_resource(UserAPI, "/api/user/")
    api.add_resource(DeckAPI, "/api/deck/", "/api/deck/<int:deck_id>")
    api.add_resource(CardAPI, "/api/card/",
                     "/api/card/<int:deck_id>", "/api/card/<int:card_id>")
    api.add_resource(ReviewAPI, "/api/review/<int:deck_id>")
    port = int(os.environ.get('PORT', 33507))

    serve(my_app, host="0.0.0.0", port=port)
