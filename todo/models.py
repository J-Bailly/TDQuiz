from todo.app import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120), nullable=True)
    done = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Task {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'done': self.done
        }


class Questionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    questions = db.relationship("Question", backref="questionnaire", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "questions": [question.to_dict() for question in self.questions]
        }


# Modèle de base pour les questions
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # "open" ou "multiple"
    questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaire.id"), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'question',
        'polymorphic_on': type
    }

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type
        }


# Question ouverte avec une réponse correcte
class OpenQuestion(Question):
    id = db.Column(db.Integer, db.ForeignKey("question.id"), primary_key=True)
    correct_answer = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'open'
    }

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "type": "open",
            "correct_answer": self.correct_answer
        }


# Question à choix multiple
class MultipleChoiceQuestion(Question):
    id = db.Column(db.Integer, db.ForeignKey("question.id"), primary_key=True)
    choices = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'multiple'
    }

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "type": "multiple",
            "choices": self.choices.split(","),
            "correct_answer": self.correct_answer
        }


# Stockage des réponses des utilisateurs
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_answer = db.Column(db.String(255), nullable=False)
