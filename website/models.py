from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

# from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    displayname: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    is_authenticated: Mapped[bool] = mapped_column(default=False)
    # is_authenticated = False
    is_active: Mapped[bool] = mapped_column(default=True)
    is_anonymous: Mapped[bool] = mapped_column(default=False)

    def get_id(self):
        return str(self.id)


class AddedArtists(db.Model):
    __tablename__ = "addedArtist"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    artist_id: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    tag: Mapped[str] = mapped_column(nullable=False)


class UserTags(db.Model):
    __tablename__ = "userTags"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    tag: Mapped[str] = mapped_column(nullable=False)


# class FlaggedMusic(db.Model):
#     __tablename__ = "flaggedMusic"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     album_id: Mapped[str] = mapped_column(nullable=False)
