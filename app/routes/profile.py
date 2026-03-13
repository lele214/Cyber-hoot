# import de Flask et des éléments qu'on utilise (les routes, les affichages html, la session, les redirections, les messages flash)
from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from app.models.models import (
    Result,
    Quiz,
    User,
    Role,
    Badge,
    Question,
    Response,
    Media,
    ConnectionLog,
    Notification,
    UserBadge,
    UserToRole,
    Review,
)
from app.extensions import db, db_transaction
from app.decorators import login_required, role_required
from app.routes.auth import generate_reset_token
from werkzeug.utils import secure_filename
from datetime import date
from app.services.virustotal import scan_file, VirusTotalError
import uuid
import os


# Fonction pour ajouter des images (en cours/en test)
def allowed_file(filename):
    """Vérifie que l'extension du fichier est autorisée."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_upload(file):
    """Sauvegarde un fichier uploadé après scan VirusTotal. Lève VirusTotalError si rejeté."""
    ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    file.save(filepath)
    try:
        scan_file(filepath)
    except VirusTotalError:
        os.remove(filepath)
        raise
    return unique_name


# Création de la route liée aux profils utilisateurs
profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


# Envoie vers la page de profil par défaut (redirige automatiquement vers le profil Player)
@profile_bp.get("/")
@login_required
def profile():
    # Vérifie si l'utilisateur est connecté en cherchant son ID dans la session
    # if "user_id" not in session:
    #     return redirect(url_for("auth.login_get"))

    # Rediriger par défaut vers le profil Player
    return redirect(url_for("profile.player_dashboard"))


# Envoie vers la page du tableau de bord administrateur
@profile_bp.get("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    # Vérifie si l'utilisateur est connecté
    # if "user_id" not in session:
    #     return redirect(url_for("auth.login_get"))

    # Récupère les rôles de l'utilisateur depuis la session
    user_roles = session.get("user_roles", [])
    # Vérifie si l'utilisateur possède le rôle "admin"
    # if "admin" not in user_roles:
    #     flash("Accès refusé : réservé aux administrateurs", "error")
    #     return redirect(url_for("main.home"))

    # Récupère le nom d'utilisateur depuis la session
    username = session.get("username")

    # --- Statistiques générales ---
    total_users = User.query.count()
    total_quizzes = Quiz.query.count()
    published_quizzes = Quiz.query.filter_by(statut="PUBLISHED").count()

    # Score moyen global (tous les utilisateurs)
    all_results = Result.query.filter(Result.totalQuestions > 0).all()
    if all_results:
        global_avg = round(
            sum(r.score / r.totalQuestions * 100 for r in all_results)
            / len(all_results),
            1,
        )
    else:
        global_avg = 0

    # --- Liste des utilisateurs avec leurs rôles ---
    users = User.query.all()
    users_data = []
    for user in users:
        user_role_names = [role.nameRoles for role in user.roles]
        users_data.append(
            {
                "id": user.idUSER,
                "username": user.username,
                "email": user.emailUser,
                "roles": user_role_names,
            }
        )

    # --- Liste des quiz avec le créateur ---
    quizzes = (
        db.session.query(Quiz, User)
        .join(User, Quiz.idCreatedByUser == User.idUSER)
        .order_by(Quiz.createdAt.desc())
        .all()
    )
    quizzes_data = []
    for quiz, creator in quizzes:
        quizzes_data.append(
            {
                "id": quiz.idQUIZ,
                "title": quiz.title,
                "creator": creator.username,
                "difficulty": quiz.difficulty,
                "statut": quiz.statut,
                "category": QUIZ_CATEGORIES.get(quiz.category, "—")
                if quiz.category
                else "—",
                "date": quiz.createdAt.strftime("%d/%m/%Y")
                if quiz.createdAt
                else "N/A",
            }
        )

    # --- Liste des badges ---
    all_badges = Badge.query.order_by(Badge.trigger, Badge.category, Badge.score_min).all()
    badges_data = []
    TRIGGER_LABELS = {
        "score": "Score",
        "review": "Avis",
        "review_comment": "Avis + commentaire",
    }
    CATEGORY_LABELS = {
        "SECURITE_WEB": "Sécurité Web",
        "MALWARE": "Malware",
        "RESEAUX": "Réseaux",
        "CRYPTOGRAPHIE": "Cryptographie",
        "INGENIERIE_SOCIALE": "Ingénierie sociale",
        "INTRODUCTION_CYBER": "Introduction Cyber",
    }
    for badge in all_badges:
        badges_data.append(
            {
                "id": badge.idBadges,
                "name": badge.name,
                "icon": badge.icon or "🏅",
                "description": badge.description or "",
                "trigger": TRIGGER_LABELS.get(badge.trigger, badge.trigger),
                "category": CATEGORY_LABELS.get(badge.category, "Global") if badge.category else "Global",
                "score_range": f"{badge.score_min}% – {badge.score_max}%"
                    if badge.score_min is not None and badge.score_max is not None
                    else "—",
            }
        )

    # --- Statistiques par catégorie (nombre de parties jouées) ---
    category_stats = {}
    for key, label in QUIZ_CATEGORIES.items():
        count = (
            db.session.query(Result)
            .join(Quiz, Result.idQUIZinResult == Quiz.idQUIZ)
            .filter(Quiz.category == key)
            .count()
        )
        category_stats[label] = count

    # --- Quiz en attente de validation ---
    pending_quizzes = (
        db.session.query(Quiz, User)
        .join(User, Quiz.idCreatedByUser == User.idUSER)
        .filter(Quiz.statut == "PENDING")
        .order_by(Quiz.createdAt.desc())
        .all()
    )
    pending_data = []
    for quiz, creator in pending_quizzes:
        pending_data.append(
            {
                "id": quiz.idQUIZ,
                "title": quiz.title,
                "creator": creator.username,
                "difficulty": quiz.difficulty,
                "questions_count": len(quiz.questions),
                "date": quiz.createdAt.strftime("%d/%m/%Y")
                if quiz.createdAt
                else "N/A",
            }
        )

    # Affiche le template du dashboard admin avec les données
    return render_template(
        "profile/admin/admin_dashboard.html",
        username=username,
        user_roles=user_roles,
        total_users=total_users,
        total_quizzes=total_quizzes,
        published_quizzes=published_quizzes,
        global_avg=global_avg,
        users_data=users_data,
        quizzes_data=quizzes_data,
        badges_data=badges_data,
        pending_data=pending_data,
        quiz_categories=QUIZ_CATEGORIES,
        category_stats=category_stats,
    )


# Envoie vers la page du tableau de bord créateur
@profile_bp.get("/creator")
@login_required
@role_required("creator")
def creator_dashboard():
    # Vérifie si l'utilisateur est connecté
    # if "user_id" not in session:
    #     return redirect(url_for("auth.login_get"))

    # Récupère les rôles de l'utilisateur depuis la session
    user_roles = session.get("user_roles", [])
    # Vérifie si l'utilisateur possède le rôle "creator"
    # if "creator" not in user_roles:
    #     flash("Accès refusé : réservé aux créateurs", "error")
    #     return redirect(url_for("main.home"))

    # Récupère le nom d'utilisateur depuis la session
    username = session.get("username")
    user_id = session.get("user_id")

    # --- Statistiques du créateur ---
    # Quiz créés par ce créateur
    creator_quizzes = Quiz.query.filter_by(idCreatedByUser=user_id).all()
    total_created = len(creator_quizzes)
    published_count = sum(1 for q in creator_quizzes if q.statut == "PUBLISHED")
    draft_count = sum(1 for q in creator_quizzes if q.statut == "DRAFT")

    # --- Liste des quiz du créateur avec statistiques ---
    quizzes_data = []
    for quiz in creator_quizzes:
        # Nombre de joueurs ayant complété ce quiz
        players_count = Result.query.filter_by(idQUIZinResult=quiz.idQUIZ).count()
        # Score moyen sur ce quiz
        quiz_results = Result.query.filter(
            Result.idQUIZinResult == quiz.idQUIZ,
            Result.totalQuestions > 0,
        ).all()
        if quiz_results:
            avg_score = round(
                sum(r.score / r.totalQuestions * 100 for r in quiz_results)
                / len(quiz_results),
                1,
            )
        else:
            avg_score = 0

        # Nombre de questions dans ce quiz
        questions_count = len(quiz.questions)

        quizzes_data.append(
            {
                "id": quiz.idQUIZ,
                "title": quiz.title,
                "difficulty": quiz.difficulty,
                "statut": quiz.statut,
                "date": quiz.createdAt.strftime("%d/%m/%Y")
                if quiz.createdAt
                else "N/A",
                "players_count": players_count,
                "avg_score": avg_score,
                "questions_count": questions_count,
            }
        )

    # Affiche le template du dashboard créateur avec les données
    return render_template(
        "profile/creator/creator_dashboard.html",
        username=username,
        user_roles=user_roles,
        total_created=total_created,
        published_count=published_count,
        draft_count=draft_count,
        quizzes_data=quizzes_data,
    )


# Envoie vers la page du tableau de bord joueur
@profile_bp.get("/player")
@login_required
def player_dashboard():
    # Vérifie si l'utilisateur est connecté
    # if "user_id" not in session:
    #     return redirect(url_for("auth.login_get"))

    # Récupère le nom d'utilisateur et les rôles depuis la session
    username = session.get("username")
    user_roles = session.get("user_roles", [])
    user_id = session.get("user_id")

    # Récupérer les statistiques de l'utilisateur
    # 1. Nombre total de quiz disponibles (publiés)
    total_quizzes = Quiz.query.filter_by(statut="PUBLISHED").count()

    # 2. Récupérer tous les résultats de l'utilisateur avec les informations du quiz
    user_results = (
        db.session.query(Result, Quiz)
        .join(Quiz, Result.idQUIZinResult == Quiz.idQUIZ)
        .filter(Result.idUSERinResult == user_id)
        .order_by(Result.date.desc())
        .all()
    )

    # 3. Calculer les statistiques
    completed_quizzes = len(user_results)
    remaining_quizzes = total_quizzes - completed_quizzes

    # 4. Calculer le score moyen
    if completed_quizzes > 0:
        total_score = sum(
            (result.score / result.totalQuestions * 100)
            for result, quiz in user_results
            if result.totalQuestions > 0
        )
        average_score = round(total_score / completed_quizzes, 1)
    else:
        average_score = 0

    # 5. Formater les résultats pour l'affichage
    # Récupère les quiz déjà notés par l'utilisateur
    reviewed_quiz_ids = {
        r.idQUIZinReview
        for r in Review.query.filter_by(idUSERinReview=user_id).all()
    }

    quiz_history = []
    for result, quiz in user_results:
        if result.totalQuestions > 0:
            percentage = round((result.score / result.totalQuestions) * 100)
        else:
            percentage = 0

        quiz_history.append(
            {
                "quiz_id": quiz.idQUIZ,
                "quiz_title": quiz.title,
                "quiz_difficulty": quiz.difficulty,
                "score": result.score,
                "total_questions": result.totalQuestions,
                "percentage": percentage,
                "date": result.date.strftime("%d/%m/%Y") if result.date else "N/A",
                "has_review": quiz.idQUIZ in reviewed_quiz_ids,
            }
        )

    # 6. Récupérer les badges de l'utilisateur
    user_badges_data = (
        db.session.query(UserBadge, Badge)
        .join(Badge, UserBadge.idBadge == Badge.idBadges)
        .filter(UserBadge.idUser == user_id)
        .order_by(UserBadge.obtainedAt.desc())
        .all()
    )
    badges = [
        {
            "name": badge.name,
            "description": badge.description,
            "icon": badge.icon,
            "obtained_at": user_badge.obtainedAt.strftime("%d/%m/%Y") if user_badge.obtainedAt else "N/A",
        }
        for user_badge, badge in user_badges_data
    ]

    # Affiche le template du dashboard joueur avec les données de l'utilisateur
    return render_template(
        "profile/player/player_dashboard.html",
        username=username,
        user_roles=user_roles,
        total_quizzes=total_quizzes,
        completed_quizzes=completed_quizzes,
        remaining_quizzes=remaining_quizzes,
        average_score=average_score,
        quiz_history=quiz_history,
        badges=badges,
    )


# Affiche le formulaire de création de quiz
@profile_bp.get("/creator/quiz/create")
@login_required
@role_required("creator")
def creator_quiz_create():
    # Vérifie si l'utilisateur est connecté
    # if "user_id" not in session:
    #     return redirect(url_for("auth.login_get"))

    # Vérifie si l'utilisateur possède le rôle "creator"
    # user_roles = session.get("user_roles", [])
    # if "creator" not in user_roles:
    #     flash("Accès refusé : réservé aux créateurs", "error")
    #     return redirect(url_for("main.home"))

    return render_template("profile/creator/creator_quiz_create.html")


# Traite la soumission du formulaire de création de quiz
@profile_bp.post("/creator/quiz/create")
@login_required
@role_required("creator")
def creator_quiz_create_post():
    # Vérifie si l'utilisateur est connecté
    # if "user_id" not in session:
    #     return redirect(url_for("auth.login_get"))

    # Vérifie si l'utilisateur possède le rôle "creator"
    # user_roles = session.get("user_roles", [])
    # if "creator" not in user_roles:
    #     flash("Accès refusé : réservé aux créateurs", "error")
    #     return redirect(url_for("main.home"))

    # Récupère les données du formulaire
    title = request.form.get("title", "").strip()
    difficulty = request.form.get("difficulty")

    # Validation des champs
    if not title:
        flash("Le titre du quiz est obligatoire", "error")
        return render_template("profile/creator/creator_quiz_create.html")

    if difficulty not in ("EASY", "MEDIUM", "HARD"):
        flash("Veuillez sélectionner une difficulté valide", "error")
        return render_template("profile/creator/creator_quiz_create.html")

    # Récupérer les questions depuis le formulaire
    questions_data = []
    q_index = 0
    while True:
        question_text = request.form.get(f"question_text_{q_index}", "").strip()
        if not question_text:
            # Plus de questions à traiter (index non trouvé)
            if f"question_text_{q_index}" not in request.form:
                break
            # Question vide mais présente dans le formulaire, on passe
            q_index += 1
            continue

        # Récupérer les réponses de cette question
        responses_data = []
        correct_index = request.form.get(f"correct_{q_index}", "0")
        r_index = 0
        while True:
            # response_exists est le champ caché ajouté par le JS pour chaque ligne de réponse
            if f"response_exists_{q_index}_{r_index}" not in request.form:
                break
            response_text = request.form.get(
                f"response_text_{q_index}_{r_index}", ""
            ).strip()
            responses_data.append(
                {
                    "text": response_text,
                    "is_correct": str(r_index) == correct_index,
                    "form_rindex": r_index,
                }
            )
            r_index += 1

        if len(responses_data) < 2:
            flash(
                f"La question « {question_text} » doit avoir au moins 2 réponses",
                "error",
            )
            return render_template("profile/creator/creator_quiz_create.html")

        questions_data.append(
            {
                "text": question_text,
                "responses": responses_data,
                "form_index": q_index,
            }
        )
        q_index += 1

    if not questions_data:
        flash("Veuillez ajouter au moins une question", "error")
        return render_template("profile/creator/creator_quiz_create.html")

    # Création du quiz, des questions et des réponses en base de données
    try:
        with db_transaction() as db_session:
            new_quiz = Quiz(
                title=title,
                difficulty=difficulty,
                statut="DRAFT",
                createdAt=date.today(),
                idCreatedByUser=session.get("user_id"),
            )
            db_session.add(new_quiz)
            db_session.flush()  # Pour obtenir l'ID du quiz

            for q_data in questions_data:
                new_question = Question(
                    QuestionText=q_data["text"],
                    idQuestionFromQuiz=new_quiz.idQUIZ,
                )
                db_session.add(new_question)
                db_session.flush()  # Pour obtenir l'ID de la question

                # Gérer l'image optionnelle de la question
                file_key = f"question_image_{q_data['form_index']}"
                file = request.files.get(file_key)
                if file and file.filename and allowed_file(file.filename):
                    filename = save_upload(file)
                    new_media = Media(
                        mediaUrl=filename,
                        mediaType=file.content_type,
                        idMediaFromQuestion=new_question.idQUESTION,
                    )
                    db_session.add(new_media)

                # Gérer le lien ressource optionnel de la question
                link_url = request.form.get(f"question_link_url_{q_data['form_index']}", "").strip()
                link_label = request.form.get(f"question_link_label_{q_data['form_index']}", "").strip()
                if link_url and link_url.startswith(("http://", "https://")):
                    db_session.add(
                        Media(
                            mediaUrl=link_url,
                            mediaType="link",
                            mediaLabel=link_label or link_url,
                            idMediaFromQuestion=new_question.idQUESTION,
                        )
                    )

                for r_data in q_data["responses"]:
                    new_response = Response(
                        responseText=r_data["text"],
                        isCorrect=r_data["is_correct"],
                        idResponseFromQuestion=new_question.idQUESTION,
                    )
                    db_session.add(new_response)
                    db_session.flush()

                    # Gérer l'image optionnelle de la réponse
                    file_key = (
                        f"response_image_{q_data['form_index']}_{r_data['form_rindex']}"
                    )
                    file = request.files.get(file_key)
                    if file and file.filename and allowed_file(file.filename):
                        filename = save_upload(file)
                        db_session.add(
                            Media(
                                mediaUrl=filename,
                                mediaType=file.content_type,
                                idMediaFromResponse=new_response.idRESPONSE,
                            )
                        )
    except VirusTotalError as e:
        flash(str(e), "error")
        return render_template("profile/creator/creator_quiz_create.html")

    flash("Quiz créé avec succès !", "success")
    return redirect(url_for("profile.creator_dashboard"))


# Affiche le formulaire de modification d'un quiz (pré-rempli)
@profile_bp.get("/creator/quiz/<int:quiz_id>/edit")
@login_required
@role_required("creator")
def creator_quiz_edit(quiz_id):
    # Récupère le quiz et vérifie qu'il appartient au créateur connecté
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.idCreatedByUser != session.get("user_id"):
        flash("Vous ne pouvez modifier que vos propres quiz", "error")
        return redirect(url_for("profile.creator_dashboard"))

    # Prépare les données des questions et réponses pour le template
    questions_data = []
    for question in quiz.questions:
        responses = []
        for response in question.responses:
            resp_media = Media.query.filter_by(
                idMediaFromResponse=response.idRESPONSE
            ).first()
            responses.append(
                {
                    "text": response.responseText,
                    "is_correct": response.isCorrect,
                    "media_id": resp_media.idMEDIA if resp_media else None,
                }
            )
        q_medias = Media.query.filter_by(idMediaFromQuestion=question.idQUESTION).all()
        image_media = next((m for m in q_medias if m.mediaType != "link"), None)
        link_media = next((m for m in q_medias if m.mediaType == "link"), None)
        questions_data.append(
            {
                "text": question.QuestionText,
                "responses": responses,
                "media_id": image_media.idMEDIA if image_media else None,
                "link_url": link_media.mediaUrl if link_media else "",
                "link_label": link_media.mediaLabel if link_media else "",
            }
        )

    return render_template(
        "profile/creator/creator_quiz_edit.html",
        quiz=quiz,
        questions_data=questions_data,
    )


# Traite la soumission du formulaire de modification d'un quiz
@profile_bp.post("/creator/quiz/<int:quiz_id>/edit")
@login_required
@role_required("creator")
def creator_quiz_edit_post(quiz_id):
    # Récupère le quiz et vérifie qu'il appartient au créateur connecté
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.idCreatedByUser != session.get("user_id"):
        flash("Vous ne pouvez modifier que vos propres quiz", "error")
        return redirect(url_for("profile.creator_dashboard"))

    # Récupère les données du formulaire
    title = request.form.get("title", "").strip()
    difficulty = request.form.get("difficulty")

    # Validation des champs
    if not title:
        flash("Le titre du quiz est obligatoire", "error")
        return redirect(url_for("profile.creator_quiz_edit", quiz_id=quiz_id))

    if difficulty not in ("EASY", "MEDIUM", "HARD"):
        flash("Veuillez sélectionner une difficulté valide", "error")
        return redirect(url_for("profile.creator_quiz_edit", quiz_id=quiz_id))

    # Récupérer les questions depuis le formulaire (même logique que la création)
    questions_data = []
    q_index = 0
    while True:
        question_text = request.form.get(f"question_text_{q_index}", "").strip()
        if not question_text:
            if f"question_text_{q_index}" not in request.form:
                break
            q_index += 1
            continue

        responses_data = []
        correct_index = request.form.get(f"correct_{q_index}", "0")
        r_index = 0
        while True:
            if f"response_exists_{q_index}_{r_index}" not in request.form:
                break
            response_text = request.form.get(
                f"response_text_{q_index}_{r_index}", ""
            ).strip()
            responses_data.append(
                {
                    "text": response_text,
                    "is_correct": str(r_index) == correct_index,
                    "form_rindex": r_index,
                }
            )
            r_index += 1

        if len(responses_data) < 2:
            flash(
                f"La question « {question_text} » doit avoir au moins 2 réponses",
                "error",
            )
            return redirect(url_for("profile.creator_quiz_edit", quiz_id=quiz_id))

        questions_data.append(
            {
                "text": question_text,
                "responses": responses_data,
                "form_index": q_index,
            }
        )
        q_index += 1

    if not questions_data:
        flash("Veuillez ajouter au moins une question", "error")
        return redirect(url_for("profile.creator_quiz_edit", quiz_id=quiz_id))

    # Mise à jour du quiz en base de données
    try:
        with db_transaction() as db_session:
            # Met à jour les infos du quiz
            quiz.title = title
            quiz.difficulty = difficulty
            if quiz.statut == "PUBLISHED":
                quiz.statut = "MODIFIED"

            # Supprime les anciens médias (question + réponse) du disque + de la DB
            question_ids = [
                q.idQUESTION
                for q in Question.query.filter_by(idQuestionFromQuiz=quiz.idQUIZ).all()
            ]
            if question_ids:
                # Médias des questions
                for m in Media.query.filter(
                    Media.idMediaFromQuestion.in_(question_ids)
                ).all():
                    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], m.mediaUrl)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                Media.query.filter(Media.idMediaFromQuestion.in_(question_ids)).delete(
                    synchronize_session=False
                )

                # Médias des réponses
                response_ids = [
                    r.idRESPONSE
                    for r in Response.query.filter(
                        Response.idResponseFromQuestion.in_(question_ids)
                    ).all()
                ]
                if response_ids:
                    for m in Media.query.filter(
                        Media.idMediaFromResponse.in_(response_ids)
                    ).all():
                        filepath = os.path.join(
                            current_app.config["UPLOAD_FOLDER"], m.mediaUrl
                        )
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    Media.query.filter(Media.idMediaFromResponse.in_(response_ids)).delete(
                        synchronize_session=False
                    )

                Response.query.filter(
                    Response.idResponseFromQuestion.in_(question_ids)
                ).delete(synchronize_session=False)
                Question.query.filter(Question.idQuestionFromQuiz == quiz.idQUIZ).delete(
                    synchronize_session=False
                )

            db_session.flush()

            # Recrée les nouvelles questions, réponses et médias
            for q_data in questions_data:
                new_question = Question(
                    QuestionText=q_data["text"],
                    idQuestionFromQuiz=quiz.idQUIZ,
                )
                db_session.add(new_question)
                db_session.flush()

                # Gérer l'image optionnelle de la question
                file_key = f"question_image_{q_data['form_index']}"
                file = request.files.get(file_key)
                if file and file.filename and allowed_file(file.filename):
                    filename = save_upload(file)
                    db_session.add(
                        Media(
                            mediaUrl=filename,
                            mediaType=file.content_type,
                            idMediaFromQuestion=new_question.idQUESTION,
                        )
                    )

                # Gérer le lien ressource optionnel de la question
                link_url = request.form.get(f"question_link_url_{q_data['form_index']}", "").strip()
                link_label = request.form.get(f"question_link_label_{q_data['form_index']}", "").strip()
                if link_url and link_url.startswith(("http://", "https://")):
                    db_session.add(
                        Media(
                            mediaUrl=link_url,
                            mediaType="link",
                            mediaLabel=link_label or link_url,
                            idMediaFromQuestion=new_question.idQUESTION,
                        )
                    )

                for r_data in q_data["responses"]:
                    new_response = Response(
                        responseText=r_data["text"],
                        isCorrect=r_data["is_correct"],
                        idResponseFromQuestion=new_question.idQUESTION,
                    )
                    db_session.add(new_response)
                    db_session.flush()

                    # Gérer l'image optionnelle de la réponse
                    file_key = (
                        f"response_image_{q_data['form_index']}_{r_data['form_rindex']}"
                    )
                    file = request.files.get(file_key)
                    if file and file.filename and allowed_file(file.filename):
                        filename = save_upload(file)
                        db_session.add(
                            Media(
                                mediaUrl=filename,
                                mediaType=file.content_type,
                                idMediaFromResponse=new_response.idRESPONSE,
                            )
                        )
    except VirusTotalError as e:
        flash(str(e), "error")
        return redirect(url_for("profile.creator_quiz_edit", quiz_id=quiz_id))

    flash("Quiz modifié avec succès !", "success")
    return redirect(url_for("profile.creator_dashboard"))


# Envoie un quiz en attente de validation par un admin (statut PENDING)
@profile_bp.post("/creator/quiz/<int:quiz_id>/publish")
@login_required
@role_required("creator")
def creator_quiz_publish(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.idCreatedByUser != session.get("user_id"):
        flash("Vous ne pouvez soumettre que vos propres quiz", "error")
        return redirect(url_for("profile.creator_dashboard"))

    # Vérifie qu'il y a au moins une question
    if len(quiz.questions) == 0:
        flash("Impossible de soumettre un quiz sans questions", "error")
        return redirect(url_for("profile.creator_dashboard"))

    with db_transaction():
        quiz.statut = "PENDING"

    flash("Quiz envoyé pour validation par un administrateur !", "success")
    return redirect(url_for("profile.creator_dashboard"))


# Supprime un quiz et toutes ses questions/réponses
@profile_bp.post("/creator/quiz/<int:quiz_id>/delete")
@login_required
@role_required("creator")
def creator_quiz_delete(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.idCreatedByUser != session.get("user_id"):
        flash("Vous ne pouvez supprimer que vos propres quiz", "error")
        return redirect(url_for("profile.creator_dashboard"))

    with db_transaction() as db_session:
        question_ids = [
            q.idQUESTION
            for q in Question.query.filter_by(idQuestionFromQuiz=quiz.idQUIZ).all()
        ]
        if question_ids:
            # Supprimer les fichiers média (questions + réponses) du disque
            for m in Media.query.filter(
                Media.idMediaFromQuestion.in_(question_ids)
            ).all():
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], m.mediaUrl)
                if os.path.exists(filepath):
                    os.remove(filepath)
            Media.query.filter(Media.idMediaFromQuestion.in_(question_ids)).delete(
                synchronize_session=False
            )

            response_ids = [
                r.idRESPONSE
                for r in Response.query.filter(
                    Response.idResponseFromQuestion.in_(question_ids)
                ).all()
            ]
            if response_ids:
                for m in Media.query.filter(
                    Media.idMediaFromResponse.in_(response_ids)
                ).all():
                    filepath = os.path.join(
                        current_app.config["UPLOAD_FOLDER"], m.mediaUrl
                    )
                    if os.path.exists(filepath):
                        os.remove(filepath)
                Media.query.filter(Media.idMediaFromResponse.in_(response_ids)).delete(
                    synchronize_session=False
                )

            Response.query.filter(
                Response.idResponseFromQuestion.in_(question_ids)
            ).delete(synchronize_session=False)
            Question.query.filter(Question.idQuestionFromQuiz == quiz.idQUIZ).delete(
                synchronize_session=False
            )
        Result.query.filter_by(idQUIZinResult=quiz.idQUIZ).delete(
            synchronize_session=False
        )
        db_session.delete(quiz)

    flash("Quiz supprimé avec succès !", "success")
    return redirect(url_for("profile.creator_dashboard"))


# ============================================================
# Routes Admin : validation des quiz
# ============================================================

# Liste des catégories disponibles (utilisée dans le template admin)
QUIZ_CATEGORIES = {
    "SECURITE_WEB": "Sécurité Web",
    "MALWARE": "Malware",
    "RESEAUX": "Réseaux",
    "CRYPTOGRAPHIE": "Cryptographie",
    "INGENIERIE_SOCIALE": "Ingénierie sociale",
    "INTRODUCTION_CYBER": "Introduction à la cybersécurité",
}


# Valide un quiz en attente (admin assigne une catégorie et publie)
@profile_bp.post("/admin/quiz/<int:quiz_id>/approve")
@login_required
@role_required("admin")
def admin_quiz_approve(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if quiz.statut != "PENDING":
        flash("Ce quiz n'est pas en attente de validation", "error")
        return redirect(url_for("profile.admin_dashboard"))

    category = request.form.get("category")
    if category not in QUIZ_CATEGORIES:
        flash("Veuillez sélectionner une catégorie valide", "error")
        return redirect(url_for("profile.admin_dashboard"))

    with db_transaction():
        quiz.category = category
        quiz.statut = "PUBLISHED"

    flash(
        f"Quiz « {quiz.title} » validé et publié dans la catégorie {QUIZ_CATEGORIES[category]} !",
        "success",
    )
    return redirect(url_for("profile.admin_dashboard"))


# Refuse un quiz en attente (remet en brouillon)
@profile_bp.post("/admin/quiz/<int:quiz_id>/reject")
@login_required
@role_required("admin")
def admin_quiz_reject(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if quiz.statut != "PENDING":
        flash("Ce quiz n'est pas en attente de validation", "error")
        return redirect(url_for("profile.admin_dashboard"))

    with db_transaction():
        quiz.statut = "DRAFT"

    flash(f"Quiz « {quiz.title} » refusé et remis en brouillon", "success")
    return redirect(url_for("profile.admin_dashboard"))


# ============================================================
# Routes Admin : gestion des quiz (modifier, archiver, supprimer)
# ============================================================


# Supprime un quiz (admin — pas de vérification de propriété)
@profile_bp.post("/admin/quiz/<int:quiz_id>/delete")
@login_required
@role_required("admin")
def admin_quiz_delete(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    with db_transaction() as db_session:
        question_ids = [
            q.idQUESTION
            for q in Question.query.filter_by(idQuestionFromQuiz=quiz.idQUIZ).all()
        ]
        if question_ids:
            # Supprimer les fichiers média (questions + réponses) du disque
            for m in Media.query.filter(
                Media.idMediaFromQuestion.in_(question_ids)
            ).all():
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], m.mediaUrl)
                if os.path.exists(filepath):
                    os.remove(filepath)
            Media.query.filter(Media.idMediaFromQuestion.in_(question_ids)).delete(
                synchronize_session=False
            )

            response_ids = [
                r.idRESPONSE
                for r in Response.query.filter(
                    Response.idResponseFromQuestion.in_(question_ids)
                ).all()
            ]
            if response_ids:
                for m in Media.query.filter(
                    Media.idMediaFromResponse.in_(response_ids)
                ).all():
                    filepath = os.path.join(
                        current_app.config["UPLOAD_FOLDER"], m.mediaUrl
                    )
                    if os.path.exists(filepath):
                        os.remove(filepath)
                Media.query.filter(Media.idMediaFromResponse.in_(response_ids)).delete(
                    synchronize_session=False
                )

            Response.query.filter(
                Response.idResponseFromQuestion.in_(question_ids)
            ).delete(synchronize_session=False)
            Question.query.filter(Question.idQuestionFromQuiz == quiz.idQUIZ).delete(
                synchronize_session=False
            )
        Result.query.filter_by(idQUIZinResult=quiz.idQUIZ).delete(
            synchronize_session=False
        )
        db_session.delete(quiz)

    flash("Quiz supprimé avec succès !", "success")
    return redirect(url_for("profile.admin_dashboard"))


# Archive un quiz (remet en brouillon)
@profile_bp.post("/admin/quiz/<int:quiz_id>/archive")
@login_required
@role_required("admin")
def admin_quiz_archive(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    with db_transaction():
        quiz.statut = "DRAFT"

    flash(f"Quiz « {quiz.title} » archivé (remis en brouillon)", "success")
    return redirect(url_for("profile.admin_dashboard"))


# Affiche le formulaire de modification d'un quiz (admin)
@profile_bp.get("/admin/quiz/<int:quiz_id>/edit")
@login_required
@role_required("admin")
def admin_quiz_edit(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # Prépare les données des questions et réponses pour le template
    questions_data = []
    for question in quiz.questions:
        responses = []
        for response in question.responses:
            resp_media = Media.query.filter_by(
                idMediaFromResponse=response.idRESPONSE
            ).first()
            responses.append(
                {
                    "text": response.responseText,
                    "is_correct": response.isCorrect,
                    "media_id": resp_media.idMEDIA if resp_media else None,
                }
            )
        q_medias = Media.query.filter_by(idMediaFromQuestion=question.idQUESTION).all()
        image_media = next((m for m in q_medias if m.mediaType != "link"), None)
        link_media = next((m for m in q_medias if m.mediaType == "link"), None)
        questions_data.append(
            {
                "text": question.QuestionText,
                "responses": responses,
                "media_id": image_media.idMEDIA if image_media else None,
                "link_url": link_media.mediaUrl if link_media else "",
                "link_label": link_media.mediaLabel if link_media else "",
            }
        )

    return render_template(
        "profile/creator/creator_quiz_edit.html",
        quiz=quiz,
        questions_data=questions_data,
        is_admin=True,
    )


# Traite la soumission du formulaire de modification (admin)
@profile_bp.post("/admin/quiz/<int:quiz_id>/edit")
@login_required
@role_required("admin")
def admin_quiz_edit_post(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # Récupère les données du formulaire
    title = request.form.get("title", "").strip()
    difficulty = request.form.get("difficulty")

    if not title:
        flash("Le titre du quiz est obligatoire", "error")
        return redirect(url_for("profile.admin_quiz_edit", quiz_id=quiz_id))

    if difficulty not in ("EASY", "MEDIUM", "HARD"):
        flash("Veuillez sélectionner une difficulté valide", "error")
        return redirect(url_for("profile.admin_quiz_edit", quiz_id=quiz_id))

    # Récupérer les questions depuis le formulaire
    questions_data = []
    q_index = 0
    while True:
        question_text = request.form.get(f"question_text_{q_index}", "").strip()
        if not question_text:
            if f"question_text_{q_index}" not in request.form:
                break
            q_index += 1
            continue

        responses_data = []
        correct_index = request.form.get(f"correct_{q_index}", "0")
        r_index = 0
        while True:
            if f"response_exists_{q_index}_{r_index}" not in request.form:
                break
            response_text = request.form.get(
                f"response_text_{q_index}_{r_index}", ""
            ).strip()
            responses_data.append(
                {
                    "text": response_text,
                    "is_correct": str(r_index) == correct_index,
                    "form_rindex": r_index,
                }
            )
            r_index += 1

        if len(responses_data) < 2:
            flash(
                f"La question « {question_text} » doit avoir au moins 2 réponses",
                "error",
            )
            return redirect(url_for("profile.admin_quiz_edit", quiz_id=quiz_id))

        questions_data.append(
            {
                "text": question_text,
                "responses": responses_data,
                "form_index": q_index,
            }
        )
        q_index += 1

    if not questions_data:
        flash("Veuillez ajouter au moins une question", "error")
        return redirect(url_for("profile.admin_quiz_edit", quiz_id=quiz_id))

    # Mise à jour du quiz en base de données
    try:
        with db_transaction() as db_session:
            quiz.title = title
            quiz.difficulty = difficulty

            # Supprime les anciens médias (question + réponse) du disque + de la DB
            question_ids = [
                q.idQUESTION
                for q in Question.query.filter_by(idQuestionFromQuiz=quiz.idQUIZ).all()
            ]
            if question_ids:
                # Médias des questions
                for m in Media.query.filter(
                    Media.idMediaFromQuestion.in_(question_ids)
                ).all():
                    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], m.mediaUrl)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                Media.query.filter(Media.idMediaFromQuestion.in_(question_ids)).delete(
                    synchronize_session=False
                )

                # Médias des réponses
                response_ids = [
                    r.idRESPONSE
                    for r in Response.query.filter(
                        Response.idResponseFromQuestion.in_(question_ids)
                    ).all()
                ]
                if response_ids:
                    for m in Media.query.filter(
                        Media.idMediaFromResponse.in_(response_ids)
                    ).all():
                        filepath = os.path.join(
                            current_app.config["UPLOAD_FOLDER"], m.mediaUrl
                        )
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    Media.query.filter(Media.idMediaFromResponse.in_(response_ids)).delete(
                        synchronize_session=False
                    )

                Response.query.filter(
                    Response.idResponseFromQuestion.in_(question_ids)
                ).delete(synchronize_session=False)
                Question.query.filter(Question.idQuestionFromQuiz == quiz.idQUIZ).delete(
                    synchronize_session=False
                )

            db_session.flush()

            # Recrée les nouvelles questions, réponses et médias
            for q_data in questions_data:
                new_question = Question(
                    QuestionText=q_data["text"],
                    idQuestionFromQuiz=quiz.idQUIZ,
                )
                db_session.add(new_question)
                db_session.flush()

                # Gérer l'image optionnelle de la question
                file_key = f"question_image_{q_data['form_index']}"
                file = request.files.get(file_key)
                if file and file.filename and allowed_file(file.filename):
                    filename = save_upload(file)
                    db_session.add(
                        Media(
                            mediaUrl=filename,
                            mediaType=file.content_type,
                            idMediaFromQuestion=new_question.idQUESTION,
                        )
                    )

                # Gérer le lien ressource optionnel de la question
                link_url = request.form.get(f"question_link_url_{q_data['form_index']}", "").strip()
                link_label = request.form.get(f"question_link_label_{q_data['form_index']}", "").strip()
                if link_url and link_url.startswith(("http://", "https://")):
                    db_session.add(
                        Media(
                            mediaUrl=link_url,
                            mediaType="link",
                            mediaLabel=link_label or link_url,
                            idMediaFromQuestion=new_question.idQUESTION,
                        )
                    )

                for r_data in q_data["responses"]:
                    new_response = Response(
                        responseText=r_data["text"],
                        isCorrect=r_data["is_correct"],
                        idResponseFromQuestion=new_question.idQUESTION,
                    )
                    db_session.add(new_response)
                    db_session.flush()

                    # Gérer l'image optionnelle de la réponse
                    file_key = (
                        f"response_image_{q_data['form_index']}_{r_data['form_rindex']}"
                    )
                    file = request.files.get(file_key)
                    if file and file.filename and allowed_file(file.filename):
                        filename = save_upload(file)
                        db_session.add(
                            Media(
                                mediaUrl=filename,
                                mediaType=file.content_type,
                                idMediaFromResponse=new_response.idRESPONSE,
                            )
                        )
    except VirusTotalError as e:
        flash(str(e), "error")
        return redirect(url_for("profile.admin_quiz_edit", quiz_id=quiz_id))

    flash("Quiz modifié avec succès !", "success")
    return redirect(url_for("profile.admin_dashboard"))


# ============================================================
# Routes Admin : gestion des utilisateurs
# ============================================================


# Réinitialise le mot de passe d'un utilisateur (génère un lien dans la console)
@profile_bp.post("/admin/user/<int:user_id>/reset-password")
@login_required
@role_required("admin")
def admin_user_reset_password(user_id):
    user = User.query.get_or_404(user_id)

    # Génère le token et le lien de réinitialisation
    token = generate_reset_token(user.emailUser)
    reset_url = url_for("auth.reset_password_get", token=token, _external=True)

    # Affiche le lien dans la console (mode dev)
    print(f"\n{'=' * 60}")
    print(f"  RESET MOT DE PASSE — {user.username} ({user.emailUser})")
    print(f"  Lien : {reset_url}")
    print(f"{'=' * 60}\n")

    flash(
        f"Lien de réinitialisation généré pour {user.username} (voir la console)",
        "success",
    )
    return redirect(url_for("profile.admin_dashboard"))


# Ajoute ou retire un rôle à un utilisateur
@profile_bp.post("/admin/user/<int:user_id>/assign-role")
@login_required
@role_required("admin")
def admin_user_assign_role(user_id):
    user = User.query.get_or_404(user_id)
    role_name = request.form.get("role", "").strip()

    if role_name not in ("player", "creator", "admin"):
        flash("Rôle invalide", "error")
        return redirect(url_for("profile.admin_dashboard"))

    role = Role.query.filter_by(nameRoles=role_name).first()
    if not role:
        flash(f"Le rôle « {role_name} » n'existe pas en base de données", "error")
        return redirect(url_for("profile.admin_dashboard"))

    with db_transaction():
        if role in user.roles:
            user.roles.remove(role)
            flash(f"Rôle « {role_name} » retiré à {user.username}", "success")
        else:
            user.roles.append(role)
            flash(f"Rôle « {role_name} » ajouté à {user.username}", "success")

    return redirect(url_for("profile.admin_dashboard"))


# Supprime un utilisateur et toutes ses données liées
@profile_bp.post("/admin/user/<int:user_id>/delete")
@login_required
@role_required("admin")
def admin_user_delete(user_id):
    # Empêche l'admin de se supprimer lui-même
    if user_id == session.get("user_id"):
        flash("Vous ne pouvez pas supprimer votre propre compte", "error")
        return redirect(url_for("profile.admin_dashboard"))

    user = User.query.get_or_404(user_id)
    username = user.username

    with db_transaction() as db_session:
        # Supprime les données liées (requêtes directes pour éviter les problèmes de lazy-load)
        Result.query.filter_by(idUSERinResult=user.idUSER).delete(
            synchronize_session=False
        )
        ConnectionLog.query.filter_by(idUserForConnection=user.idUSER).delete(
            synchronize_session=False
        )
        UserBadge.query.filter_by(idUser=user.idUSER).delete(synchronize_session=False)
        Notification.query.filter_by(idUser=user.idUSER).delete(
            synchronize_session=False
        )
        UserToRole.query.filter_by(idUser=user.idUSER).delete(synchronize_session=False)
        db_session.delete(user)

    flash(f"Utilisateur « {username} » supprimé avec succès", "success")
    return redirect(url_for("profile.admin_dashboard"))


# ---------------------------------------------------------------------------
# Gestion admin des badges
# ---------------------------------------------------------------------------

@profile_bp.post("/admin/badge/<int:badge_id>/delete")
@login_required
@role_required("admin")
def admin_badge_delete(badge_id):
    badge = Badge.query.get_or_404(badge_id)
    name = badge.name
    with db_transaction() as db_session:
        UserBadge.query.filter_by(idBadge=badge_id).delete(synchronize_session=False)
        db_session.delete(badge)
    flash(f"Badge « {name} » supprimé avec succès", "success")
    return redirect(url_for("profile.admin_dashboard"))


@profile_bp.route("/admin/badge/<int:badge_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_badge_edit(badge_id):
    badge = Badge.query.get_or_404(badge_id)
    if request.method == "POST":
        badge.name = request.form.get("name", badge.name).strip()
        badge.description = request.form.get("description", badge.description or "").strip() or None
        badge.icon = request.form.get("icon", badge.icon or "").strip() or None
        score_min = request.form.get("score_min", "")
        score_max = request.form.get("score_max", "")
        badge.score_min = int(score_min) if score_min.strip().isdigit() else None
        badge.score_max = int(score_max) if score_max.strip().isdigit() else None
        category = request.form.get("category", "")
        badge.category = category if category else None
        with db_transaction() as db_session:
            db_session.merge(badge)
        flash(f"Badge « {badge.name} » modifié avec succès", "success")
        return redirect(url_for("profile.admin_dashboard"))
    return render_template("profile/admin/admin_badge_edit.html", badge=badge)
