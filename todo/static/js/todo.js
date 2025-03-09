$(function () {
    let selectedQuizId = null;

    // Gestion des modes (création/réponse)
    $("#createMode").click(() => {
        $("#creationSection").show();
        $("#answerSection").hide();
    });

    $("#answerMode").click(() => {
        $("#creationSection").hide();
        $("#answerSection").show();
    });

    // Chargement des questionnaires
    $("#loadQuizzes").click(refreshQuizList);
    $("#loadAnswerQuizzes").click(refreshQuizListForAnswers);
    $("#addQuiz").click(formQuestionnaire);
    $("#submitAnswers").click(submitAnswers);
    $("#addQuestion").click(() => formQuestion(true));

    function refreshQuizList() {
        $("#currentQuiz").empty();
        fetch("/todo/api/v1.0/questionnaires")
            .then(response => response.json())
            .then(data => {
                afficherQuestionnaires(data);
            })
            .catch(err => $("#questionnaires").html("<b>Erreur de récupération !</b> " + err));
    }
    

    function refreshQuizListForAnswers() {
        $("#quizList").empty();
        fetch("/todo/api/v1.0/questionnaires")
            .then(response => response.json())
            .then(data => afficherQuizzPourReponse(data))
            .catch(err => $("#quizList").html("<b>Erreur de récupération !</b> " + err));
    }

    function afficherQuestionnaires(data) {
        $('#questionnaires').empty().append($('<ul>'));
        data.questionnaires.forEach(quiz => {
            let quizItem = $('<li>')
                .append($('<a href="#">').text(quiz.name))
                .on("click", () => afficherDetailsQuestionnaire(quiz));
            $('#questionnaires ul').append(quizItem);
        });
    }

    function afficherQuizzPourReponse(data) {
        $('#quizList').empty().append($('<ul>'));
        data.questionnaires.forEach(quiz => {
            let quizItem = $('<li>')
                .append($('<a href="#">').text(quiz.name))
                .on("click", () => afficherQuestionsPourReponse(quiz));
            $('#quizList ul').append(quizItem);
        });
    }

    function afficherDetailsQuestionnaire(quiz) {
        selectedQuizId = quiz.id;
        $("#currentQuiz").html(`
            <h3>${quiz.name}</h3>
            <button id="deleteQuiz">Supprimer</button>
        `);
        $("#addQuestion").show();
        $("#deleteQuiz").off("click").on("click", () => deleteQuiz(quiz.id));
    
        afficherQuestions(quiz.questions, quiz.id);
    }
    

    function afficherQuestions(questions, quizId) {
        console.log("Questions reçues :", questions);  // 🟢 Vérification
    
        $("#questionList").empty().append("<h3>Questions</h3>").append($('<ul>'));
        questions.forEach(q => {
            let questionItem = $('<li>')
                .append($('<span>').text(q.title + " (" + q.type + ") "))
                .append($('<button>').text("Modifier").on("click", () => formQuestion(false, q, quizId)))
                .append($('<button>').text("Supprimer").on("click", () => deleteQuestion(q.id)));
            $('#questionList ul').append(questionItem);
        });
    }
    
    

    function afficherQuestionsPourReponse(quiz) {
        selectedQuizId = quiz.id;

        $("#quizQuestions").empty().append("<h3>Questions</h3>").append($('<ul>'));

        quiz.questions.forEach(q => {
            let answerField;
            if (q.type === "open") {
                answerField = $('<input type="text">').attr("id", "answer_" + q.id);
            } else if (q.type === "multiple") {
                answerField = $('<select>').attr("id", "answer_" + q.id);
                q.choices.forEach(choice => {
                    answerField.append($('<option>').text(choice).val(choice));
                });
            }
            $("#quizQuestions").append($('<div>').append($('<label>').text(q.title), answerField));
        });
    }

    function formQuestionnaire() {
        
        let name = prompt("Nom du questionnaire ?");
        if (!name) return;
        let quiz = { name: name };

        fetch("/todo/api/v1.0/questionnaires", {
            headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
            method: "POST",
            body: JSON.stringify(quiz)
        }).then(() => refreshQuizList());
    }

    function deleteQuiz(quizId) {
        if (!confirm("Voulez-vous vraiment supprimer ce questionnaire ?")) return;
        fetch(`/todo/api/v1.0/questionnaires/${quizId}`, { method: "DELETE" })
            .then(() => refreshQuizList());
    }

    function submitAnswers() {
        if (!selectedQuizId) {
            alert("Veuillez sélectionner un questionnaire avant de soumettre.");
            return;
        }
    
        let answers = {};
        $("#quizQuestions input, #quizQuestions select").each(function () {
            let questionId = $(this).attr("id").split("_")[1];
            answers[questionId] = $(this).val();
        });
    
        fetch(`/todo/api/v1.0/questionnaires/${selectedQuizId}/submit`, {  // Ajout de l'ID du quiz
            headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
            method: "POST",
            body: JSON.stringify(answers)
        })
        .then(res => res.json())
        .then(data => {
            let message = `✅ Résultats du questionnaire :\n\n`;
            message += `🔢 Score : ${data.score} / ${data.total_questions}\n\n`;
        
            data.results.forEach((result, index) => {
                message += `🔹 Question ${index + 1}: ${result.question}\n`;
                message += `   ✏️ Votre réponse : ${result.user_answer || "Non répondu"}\n`;
                message += `   ✅ Bonne réponse : ${result.correct_answer}\n`;
                message += result.is_correct ? "   🎉 Correct !\n\n" : "   ❌ Incorrect.\n\n";
            });
        
            alert(message);
        })
        
        .catch(err => console.log(err));
    }

    function formQuestion(isNew, question = null, quizId = null) {
        if (!quizId) quizId = selectedQuizId;

        let form = `
            <h3>${isNew ? "Ajouter" : "Modifier"} une Question</h3>
            <label>Titre: <input type="text" id="questionTitle" value="${question ? question.title : ''}"></label><br>
            <label>Type:
                <select id="questionType">
                    <option value="open" ${question && question.type === "open" ? "selected" : ""}>Ouverte</option>
                    <option value="multiple" ${question && question.type === "multiple" ? "selected" : ""}>Choix multiple</option>
                </select>
            </label><br>
            <label>Choix (séparés par des virgules): <input type="text" id="questionChoices" value="${question && question.type === "multiple" ? question.choices.join(",") : ''}"></label><br>
            <label>Bonne réponse: <input type="text" id="correctAnswer" value="${question ? question.correct_answer : ''}"></label><br>
            <button id="saveQuestion">${isNew ? "Ajouter" : "Modifier"}</button>
        `;

        $("#currentQuiz").append(form);

        $("#saveQuestion").off("click").on("click", () => {
            saveQuestion(isNew, question?.id, quizId);
        });
    }

    function deleteQuestion(questionId) {
        if (!confirm("Voulez-vous vraiment supprimer cette question ?")) return;
        
        fetch(`/todo/api/v1.0/questionnaires/${selectedQuizId}/questions/${questionId}`, { method: "DELETE" })
            .then(() => {
                refreshQuizList(() => afficherDetailsQuestionnaire({ id: selectedQuizId }));
                refreshQuestionList(selectedQuizId);
            });
    }
        

    function saveQuestion(isNew, questionId, quizId) {
        let title = $("#questionTitle").val();
        let type = $("#questionType").val();
        let choices = type === "multiple" ? $("#questionChoices").val().split(",") : [];
        let correctAnswer = $("#correctAnswer").val();
        let question = { title, type, choices, correct_answer: correctAnswer };
    
        let url = isNew 
            ? `/todo/api/v1.0/questionnaires/${quizId}/questions`  
            : `/todo/api/v1.0/questionnaires/${quizId}/questions/${questionId}`;  
    
        fetch(url, {
            headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
            method: isNew ? "POST" : "PUT",
            body: JSON.stringify(question)
        })
        .then(response => response.json())
        .then(updatedQuestion => {
            refreshQuizList(() => afficherDetailsQuestionnaire({ id: quizId }));
            refreshQuestionList(quizId);
        });
            
            
    }

    function refreshQuestionList(quizId) {
        fetch(`/todo/api/v1.0/questionnaires`)
            .then(response => response.json())
            .then(data => {
                let selectedQuiz = data.questionnaires.find(q => q.id === quizId);
                if (selectedQuiz) {
                    afficherQuestions(selectedQuiz.questions, quizId);
                }
            })
            .catch(err => console.error("Erreur de récupération des questions :", err));
    }
    
    
    });