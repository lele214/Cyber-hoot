from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    return render_template("index.html")


@main_bp.get("/quiz/quiz")
def quiz():
    return render_template("quiz/quiz.html")


@main_bp.get("/quiz/<int:quiz_id>")
def quiz_detail(quiz_id):
    if quiz_id < 1 or quiz_id > 8:
        return "Quiz non trouvé", 404

    return render_template(f"quiz/quiz{quiz_id}.html")
