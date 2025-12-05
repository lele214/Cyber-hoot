from flask import Flask, jsonify, render_template_string
from database import init_db, db
from data.models import User, Quiz, Badge, Notification, Trophy, Question, Response, Media, Result, ConnexionLog

app = Flask(__name__)

# Initialiser la base de données
init_db(app)


@app.route("/")
def home():
    """Page d'accueil avec liens vers toutes les routes de test"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cyber-hoot DB Tester</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            h1 { color: #333; }
            .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .table-link {
                display: inline-block;
                margin: 10px;
                padding: 15px 25px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background 0.3s;
            }
            .table-link:hover { background: #0056b3; }
            .section { margin: 30px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Cyber-hoot - Database Tester</h1>

            <div class="section">
                <h2>📊 Vue d'ensemble</h2>
                <a href="/db/overview" class="table-link">Vue d'ensemble de la DB</a>
            </div>

            <div class="section">
                <h2>📋 Tables disponibles</h2>
                <a href="/db/users" class="table-link">👥 Users</a>
                <a href="/db/quiz" class="table-link">📝 Quiz</a>
                <a href="/db/questions" class="table-link">❓ Questions</a>
                <a href="/db/responses" class="table-link">✅ Responses</a>
                <a href="/db/badges" class="table-link">🏆 Badges</a>
                <a href="/db/trophies" class="table-link">🥇 Trophies</a>
                <a href="/db/notifications" class="table-link">🔔 Notifications</a>
                <a href="/db/results" class="table-link">📈 Results</a>
                <a href="/db/media" class="table-link">🖼️ Media</a>
                <a href="/db/logs" class="table-link">📋 Connexion Logs</a>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/db/overview")
def db_overview():
    """Vue d'ensemble de toutes les tables avec leurs counts"""
    try:
        overview = {
            "users": User.query.count(),
            "quiz": Quiz.query.count(),
            "questions": Question.query.count(),
            "responses": Response.query.count(),
            "badges": Badge.query.count(),
            "trophies": Trophy.query.count(),
            "notifications": Notification.query.count(),
            "results": Result.query.count(),
            "media": Media.query.count(),
            "connexion_logs": ConnexionLog.query.count()
        }

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Overview</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 8px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #007bff; color: white; }}
                tr:hover {{ background: #f5f5f5; }}
                .back-link {{ display: inline-block; margin: 20px 0; padding: 10px 20px;
                             background: #6c757d; color: white; text-decoration: none;
                             border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Vue d'ensemble de la base de données</h1>
                <table>
                    <tr><th>Table</th><th>Nombre d'enregistrements</th></tr>
                    <tr><td>👥 Users</td><td>{overview['users']}</td></tr>
                    <tr><td>📝 Quiz</td><td>{overview['quiz']}</td></tr>
                    <tr><td>❓ Questions</td><td>{overview['questions']}</td></tr>
                    <tr><td>✅ Responses</td><td>{overview['responses']}</td></tr>
                    <tr><td>🏆 Badges</td><td>{overview['badges']}</td></tr>
                    <tr><td>🥇 Trophies</td><td>{overview['trophies']}</td></tr>
                    <tr><td>🔔 Notifications</td><td>{overview['notifications']}</td></tr>
                    <tr><td>📈 Results</td><td>{overview['results']}</td></tr>
                    <tr><td>🖼️ Media</td><td>{overview['media']}</td></tr>
                    <tr><td>📋 Connexion Logs</td><td>{overview['connexion_logs']}</td></tr>
                </table>
                <a href="/" class="back-link">⬅️ Retour</a>
            </div>
        </body>
        </html>
        """
        return render_template_string(html)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/users")
def get_users():
    """Affiche tous les utilisateurs"""
    try:
        users = User.query.all()
        users_data = [{
            "id": u.idUSER,
            "username": u.username,
            "email": u.emailUser,
            "type": u.typeUser
        } for u in users]

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Users</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 8px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #007bff; color: white; }}
                tr:hover {{ background: #f5f5f5; }}
                .back-link {{ display: inline-block; margin: 20px 0; padding: 10px 20px;
                             background: #6c757d; color: white; text-decoration: none;
                             border-radius: 5px; }}
                .json-link {{ margin-left: 20px; padding: 10px 20px;
                             background: #28a745; color: white; text-decoration: none;
                             border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>👥 Utilisateurs ({len(users_data)})</h1>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Type</th>
                    </tr>
                    {''.join(f'<tr><td>{u["id"]}</td><td>{u["username"]}</td><td>{u["email"]}</td><td>{u["type"]}</td></tr>' for u in users_data)}
                </table>
                <a href="/" class="back-link">⬅️ Retour</a>
                <a href="/db/users/json" class="json-link">📄 Voir en JSON</a>
            </div>
        </body>
        </html>
        """
        return render_template_string(html)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/users/json")
def get_users_json():
    """Retourne les utilisateurs en JSON"""
    try:
        users = User.query.all()
        return jsonify([{
            "id": u.idUSER,
            "username": u.username,
            "email": u.emailUser,
            "type": u.typeUser
        } for u in users])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/quiz")
def get_quiz():
    """Affiche tous les quiz"""
    try:
        quizzes = Quiz.query.all()
        quiz_data = [{
            "id": q.idQUIZ,
            "title": q.title,
            "difficulty": q.difficulty,
            "status": q.statut,
            "created_by": q.idCreatedByUser,
            "created_at": str(q.createdAt) if q.createdAt else None
        } for q in quizzes]

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Quiz</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 8px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #007bff; color: white; }}
                tr:hover {{ background: #f5f5f5; }}
                .back-link {{ display: inline-block; margin: 20px 0; padding: 10px 20px;
                             background: #6c757d; color: white; text-decoration: none;
                             border-radius: 5px; }}
                .json-link {{ margin-left: 20px; padding: 10px 20px;
                             background: #28a745; color: white; text-decoration: none;
                             border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📝 Quiz ({len(quiz_data)})</h1>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Titre</th>
                        <th>Difficulté</th>
                        <th>Status</th>
                        <th>Créé par</th>
                        <th>Date</th>
                    </tr>
                    {''.join(f'<tr><td>{q["id"]}</td><td>{q["title"]}</td><td>{q["difficulty"]}</td><td>{q["status"]}</td><td>{q["created_by"]}</td><td>{q["created_at"]}</td></tr>' for q in quiz_data)}
                </table>
                <a href="/" class="back-link">⬅️ Retour</a>
                <a href="/db/quiz/json" class="json-link">📄 Voir en JSON</a>
            </div>
        </body>
        </html>
        """
        return render_template_string(html)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/quiz/json")
def get_quiz_json():
    """Retourne les quiz en JSON"""
    try:
        quizzes = Quiz.query.all()
        return jsonify([{
            "id": q.idQUIZ,
            "title": q.title,
            "difficulty": q.difficulty,
            "status": q.statut,
            "created_by": q.idCreatedByUser,
            "created_at": str(q.createdAt) if q.createdAt else None
        } for q in quizzes])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/questions")
def get_questions():
    """Affiche toutes les questions"""
    try:
        questions = Question.query.all()
        return jsonify([{
            "id": q.idQUESTION,
            "quiz_id": q.idQuestionFromQuiz,
            "text": q.QuestionText
        } for q in questions])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/responses")
def get_responses():
    """Affiche toutes les réponses"""
    try:
        responses = Response.query.all()
        return jsonify([{
            "id": r.idRESPONSE,
            "question_id": r.idResponseFromQuestion,
            "text": r.responseText,
            "is_correct": r.isCorrect
        } for r in responses])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/badges")
def get_badges():
    """Affiche tous les badges"""
    try:
        badges = Badge.query.all()
        return jsonify([{
            "id": b.idBADGES,
            "name": b.name,
            "quiz_id": b.idQuiz
        } for b in badges])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/trophies")
def get_trophies():
    """Affiche tous les trophées"""
    try:
        trophies = Trophy.query.all()
        return jsonify([{
            "id": t.idTrophy,
            "badge_id": t.idBadge,
            "user_id": t.idUser,
            "obtained_at": str(t.obtainedAt) if t.obtainedAt else None
        } for t in trophies])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/notifications")
def get_notifications():
    """Affiche toutes les notifications"""
    try:
        notifications = Notification.query.all()
        return jsonify([{
            "id": n.idNOTIFICATIONS,
            "user_id": n.idUser,
            "type": n.type,
            "message": n.message,
            "sent_at": str(n.sentAt) if n.sentAt else None
        } for n in notifications])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/results")
def get_results():
    """Affiche tous les résultats"""
    try:
        results = Result.query.all()
        return jsonify([{
            "id": r.idRESULT,
            "quiz_id": r.idQUIZinResult,
            "user_id": r.idUSERinResult,
            "date": str(r.date) if r.date else None,
            "history": r.resultHistory
        } for r in results])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/media")
def get_media():
    """Affiche tous les médias"""
    try:
        media = Media.query.all()
        return jsonify([{
            "id": m.idMEDIA,
            "question_id": m.idMediaFromQuestion,
            "response_id": m.idMediaFromResponse,
            "url": m.mediaUrl,
            "type": m.mediaType
        } for m in media])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/db/logs")
def get_logs():
    """Affiche tous les logs de connexion"""
    try:
        logs = ConnexionLog.query.all()
        return jsonify([{
            "id": l.idCONNEXION_LOG,
            "user_id": l.idUSERforConnexion
        } for l in logs])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
