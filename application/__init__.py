from flask import Flask, render_template
from config import Config
from flask_mongoengine import MongoEngine
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config["MONGODB_HOST"] = Config.DB_URI
app.config.from_object(Config)

db = MongoEngine()
db.init_app(app)
Bootstrap(app)

from application import routes
