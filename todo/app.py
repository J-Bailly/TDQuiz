from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os


app = Flask(__name__, static_folder="static", template_folder="templates")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '../instance/tasks.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Autoriser les requêtes CORS
cors = CORS(app, resources={r"/todo/api/v1.0/*": {"origins": "*"}})

# Importation des modèles et des vues (routes)
from todo import models, views

if __name__ == '__main__':
    app.run(debug=True)
