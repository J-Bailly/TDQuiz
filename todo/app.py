from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialisation de l'application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Autoriser les requêtes CORS
cors = CORS(app, resources={r"/todo/api/v1.0/*": {"origins": "*"}})

# Importation des modèles et des vues (routes)
from todo import models, views

if __name__ == '__main__':
    app.run(debug=True)
