from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    return render_template("index.html")


@main_bp.get("/quiz/quiz1")
def quiz1():
    return render_template("quiz/quiz1.html")
