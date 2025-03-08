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
    name = db.Column(db.String(120), unique=True, nullable=False)
    questions = db.relationship('Question', backref='questionnaire', lazy=True)

    def __repr__(self):
        return f'<Questionnaire {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    question_type = db.Column(db.String(20), nullable=False, default='text')
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaire.id'), nullable=False)

    def __repr__(self):
        return f'<Question {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'question_type': self.question_type
        }
