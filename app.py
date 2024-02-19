import os
import sys

import click
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

if sys.platform.startswith("win"):
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
app.config["SQLALCHEMY_DATABASE_URI"] = prefix + os.path.join(app.root_path, "data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@app.cli.command()
@click.option("--drop", is_flag=True, help="Create after drop.")
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialized database.")


@app.cli.command()
def forge():
    db.create_all()

    name = "Zero"
    movies = [
        {"title": "My Neighbor Totoro", "year": "1988"},
        {"title": "Dead Poets Society", "year": "1989"},
        {"title": "A Perfect World", "year": "1993"},
        {"title": "Leon", "year": "1994"},
        {"title": "Mahjong", "year": "1996"},
        {"title": "Swallowtail Butterfly", "year": "1996"},
        {"title": "King of Comedy", "year": "1999"},
        {"title": "Devils on the Doorstep", "year": "1999"},
        {"title": "WALL-E", "year": "2008"},
        {"title": "The Pork of Music", "year": "2012"},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m["title"], year=m["year"])
        db.session.add(movie)

    db.session.commit()
    click.echo("Done.")


@app.cli.command()
@click.option("--username", prompt=True, help="The username used to login.")
@click.option(
    "--password", prompt=True, hide_input=True, help="The password used to login."
)
def admin(username, password):
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo("Updating user...")
        user.username = username
        user.set_password(password)
    else:
        click.echo("Creating user...")
        user = User(name=username, username=username)
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo("Done.")


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    username: Mapped[str] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(60))
    year: Mapped[str] = mapped_column(String(4))


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404


@app.route("/hello")
def hello():
    return "<h1>Hello!</h1>"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not current_user.is_authenticated:
            return redirect(url_for("index"))

        title = request.form.get("title")
        year = request.form.get("year")
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("Invalid input.")
            return redirect(url_for("index"))
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash("Item created.")
        return redirect(url_for("index"))

    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


@app.route("/movie/edit/<int:movie_id>", methods=["GET", "POST"])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year")
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("Invalid input.")
            return redirect(url_for("edit", movie_id=movie_id))
        movie.title = title
        movie.year = year
        db.session.commit()
        flash("Item updated.")
        return redirect(url_for("index"))

    return render_template("edit.html", movie=movie)


@app.route("/movie/delete/<int:movie_id>", methods=["POST"])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("Item deleted.")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Invalid input.")
            return redirect(url_for("login"))

        user = User.query.first()
        if username != user.username or not user.validate_password(password):
            flash("Invalid username or password.")
            return redirect(url_for("login"))

        login_user(user)
        flash("Login success.")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Goodbye.")
    return redirect(url_for("index"))

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":

        name = request.form.get("name")
        if not name:
            flash("Invalid input.")
            return redirect(url_for("settings"))

        current_user.name = name
        db.session.commit()
        flash("Settings Updated.")
        return redirect(url_for("index"))

    return render_template("settings.html")
