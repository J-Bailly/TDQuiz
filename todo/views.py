from flask import jsonify, request, abort, render_template
from todo.app import app, db
from todo.models import Task, Questionnaire, Question

@app.route('/')
def index():
    return render_template('todo.html')


# Route pour obtenir toutes les tâches
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()  # Récupérer toutes les tâches de la base de données
    return jsonify({'tasks': [make_public_task(task) for task in tasks]})

# Route pour obtenir une tâche spécifique
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        abort(404)
    return jsonify({'task': make_public_task(task)})

# Route pour créer une nouvelle tâche
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = Task(
        title=request.json['title'],
        description=request.json.get('description', ""),
        done=False
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'task': make_public_task(task)}), 201

# Route pour modifier une tâche
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        abort(404)
    if not request.json:
        abort(400)
    task.title = request.json.get('title', task.title)
    task.description = request.json.get('description', task.description)
    task.done = request.json.get('done', task.done)
    db.session.commit()
    return jsonify({'task': make_public_task(task)})

# Route pour supprimer une tâche
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        abort(404)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'result': True})

# Route pour obtenir tous les questionnaires
@app.route('/todo/api/v1.0/questionnaires', methods=['GET'])
def get_questionnaires():
    questionnaires = Questionnaire.query.all()
    return jsonify({'questionnaires': [q.to_dict() for q in questionnaires]})

# Route pour créer un questionnaire
@app.route('/todo/api/v1.0/questionnaires', methods=['POST'])
def create_questionnaire():
    if not request.json or not 'name' in request.json:
        abort(400)
    questionnaire = Questionnaire(name=request.json['name'])
    db.session.add(questionnaire)
    db.session.commit()
    return jsonify({'questionnaire': questionnaire.to_dict()}), 201

# Route pour ajouter une question à un questionnaire
@app.route('/todo/api/v1.0/questionnaires/<int:questionnaire_id>/questions', methods=['POST'])
def add_question_to_questionnaire(questionnaire_id):
    questionnaire = Questionnaire.query.get(questionnaire_id)
    if questionnaire is None:
        abort(404)
    if not request.json or not 'title' in request.json:
        abort(400)
    question = Question(
        title=request.json['title'],
        question_type=request.json.get('question_type', 'text'),
        questionnaire_id=questionnaire_id
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({'question': question.to_dict()}), 201

# Fonction pour convertir une tâche en dictionnaire public
def make_public_task(task):
    new_task = {}
    for field in task.__table__.columns:  # Itère sur les colonnes du modèle
        new_task[field.name] = getattr(task, field.name)  # Utilise `field.name` pour accéder au nom de la colonne
    return new_task
