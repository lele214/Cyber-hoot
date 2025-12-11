from flask import Blueprint, render_template, redirect, url_for, flash, session

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    return render_template("index.html")
