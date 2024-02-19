# from sqlalchemy import Integer, String
# from sqlalchemy.orm import Mapped, mapped_column
# from werkzeug.security import check_password_hash, generate_password_hash
# from flask_login import UserMixin

# from watchlist import db

# class User(db.Model, UserMixin):
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String(20))
#     username: Mapped[str] = mapped_column(String(20), nullable=True)
#     password_hash: Mapped[str] = mapped_column(String(128), nullable=True)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def validate_password(self, password):
#         return check_password_hash(self.password_hash, password)


# class Movie(db.Model):
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     title: Mapped[str] = mapped_column(String(60))
#     year: Mapped[str] = mapped_column(String(4))

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from watchlist import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))
