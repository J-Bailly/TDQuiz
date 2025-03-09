from flask import jsonify, request, abort, render_template
from todo.app import app, db
from todo.models import Questionnaire, Question, OpenQuestion, MultipleChoiceQuestion
from flask_cors import CORS

# Autoriser les requêtes CORS
CORS(app, resources={r"/todo/api/v1.0/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('todo.html')

# Récupérer tous les questionnaires
@app.route('/todo/api/v1.0/questionnaires', methods=['GET'])
def get_questionnaires():
    questionnaires = Questionnaire.query.all()
    return jsonify({"questionnaires": [q.to_dict() for q in questionnaires]})

# Créer un questionnaire
@app.route('/todo/api/v1.0/questionnaires', methods=['POST'])
def create_questionnaire():
    if not request.json or "name" not in request.json:
        abort(400)

    questionnaire = Questionnaire(name=request.json["name"])
    db.session.add(questionnaire)
    db.session.commit()

    return jsonify({"questionnaire": questionnaire.to_dict()}), 201

# Supprimer un questionnaire
@app.route('/todo/api/v1.0/questionnaires/<int:questionnaire_id>', methods=['DELETE'])
def delete_questionnaire(questionnaire_id):
    questionnaire = Questionnaire.query.get(questionnaire_id)
    if not questionnaire:
        return jsonify({"error": "Questionnaire non trouvé"}), 404

    try:
        # Supprimer les questions associées
        Question.query.filter_by(questionnaire_id=questionnaire_id).delete()
        db.session.delete(questionnaire)
        db.session.commit()
        return jsonify({"message": "Questionnaire supprimé"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de la suppression : {str(e)}"}), 500

# Soumettre les réponses d'un questionnaire
@app.route('/todo/api/v1.0/questionnaires/<int:questionnaire_id>/submit', methods=['POST'])
def submit_questionnaire(questionnaire_id):
    data = request.get_json()
    questionnaire = Questionnaire.query.get(questionnaire_id)
    if not questionnaire:
        return jsonify({"error": "Questionnaire non trouvé"}), 404

    questions = Question.query.filter_by(questionnaire_id=questionnaire_id).all()
    
    score = 0
    results = []

    for question in questions:
        user_answer = data.get(str(question.id), "").strip().lower()
        correct_answer = getattr(question, 'correct_answer', None)
        is_correct = correct_answer and user_answer == correct_answer.strip().lower()

        if is_correct:
            score += 1

        results.append({
            "question_id": question.id,
            "question": question.title,
            "user_answer": user_answer,
            "correct_answer": correct_answer if correct_answer else "Aucune réponse enregistrée",
            "is_correct": is_correct
        })

    return jsonify({
        "message": "Résultats du questionnaire",
        "score": score,
        "total_questions": len(questions),
        "results": results
    }), 200

# Ajouter une question à un questionnaire
@app.route('/todo/api/v1.0/questionnaires/<int:questionnaire_id>/questions', methods=['POST'])
def add_question(questionnaire_id):
    questionnaire = Questionnaire.query.get(questionnaire_id)
    if not questionnaire:
        return jsonify({"error": "Questionnaire non trouvé"}), 404

    if not request.json or "title" not in request.json or "type" not in request.json:
        return jsonify({"error": "Requête invalide, champs manquants"}), 400

    try:
        if request.json["type"] == "open":
            question = OpenQuestion(
                title=request.json["title"],
                correct_answer=request.json.get("correct_answer", ""),
                questionnaire_id=questionnaire_id
            )
        elif request.json["type"] == "multiple":
            if "choices" not in request.json:
                return jsonify({"error": "Les choix sont obligatoires pour les questions à choix multiple"}), 400
            question = MultipleChoiceQuestion(
                title=request.json["title"],
                choices=",".join(request.json["choices"]),
                correct_answer=request.json.get("correct_answer", ""),
                questionnaire_id=questionnaire_id
            )
        else:
            return jsonify({"error": "Type de question invalide"}), 400

        db.session.add(question)
        db.session.commit()
        return jsonify({"message": "Question ajoutée", "question": question.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500

# Supprimer une question
@app.route('/todo/api/v1.0/questionnaires/<int:questionnaire_id>/questions/<int:question_id>', methods=['DELETE'])
def delete_question(questionnaire_id, question_id):
    question = Question.query.get(question_id)
    if not question:
        return jsonify({"error": "Question non trouvée"}), 404

    db.session.delete(question)
    db.session.commit()
    return jsonify({"message": "Question supprimée"}), 200

# Modifier une question
@app.route('/todo/api/v1.0/questionnaires/<int:questionnaire_id>/questions/<int:question_id>', methods=['PUT'])
def update_question(questionnaire_id, question_id):
    question = Question.query.get(question_id)
    if not question:
        return jsonify({"error": "Question non trouvée"}), 404

    if not request.is_json:
        return jsonify({"error": "Requête invalide : JSON attendu"}), 400

    data = request.json

    # Mise à jour des champs génériques
    if "title" in data:
        question.title = data["title"]

    # Mise à jour des questions à choix multiples
    if hasattr(question, "choices") and "choices" in data:
        question.choices = ",".join(data["choices"])

    # Mise à jour de la bonne réponse
    if hasattr(question, "correct_answer") and "correct_answer" in data:
        question.correct_answer = data["correct_answer"]

    db.session.commit()
    return jsonify({"message": "Question mise à jour avec succès", "question": question.to_dict()})
