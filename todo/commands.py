from todo.app import app
from todo.models import db, Questionnaire, Question

@app.cli.command('initdb')
def init_db():
    db.create_all()
    db.session.add(Questionnaire(name="Maths"))
    db.session.add(Question(title="What is 2 + 2?", questionType="MCQ", questionnaire_id=1))
    db.session.commit()
    print("Initialized the database with some test data.")
