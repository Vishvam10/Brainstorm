from .database import db


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=True)


class Deck(db.Model):
    __tablename__ = "deck"
    deck_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), nullable=False)


class Card(db.Model):
    __tablename__ = "card"
    card_id = db.Column(db.Integer, primary_key=True,
                        autoincrement=True, unique=True)
    question = db.Column(db.String)
    answer = db.Column(db.String)
    deck_id = db.Column(db.Integer, db.ForeignKey(
        "deck.deck_id"), nullable=False)


class Review(db.Model):
    __tablename__ = "review"
    review_id = db.Column(db.Integer, primary_key=True,
                          autoincrement=True, unique=True)
    deck_id = db.Column(db.Integer, db.ForeignKey(
        "deck.deck_id"), nullable=False)
    total_q = db.Column(db.Integer)
    easy_q = db.Column(db.Integer)
    medium_q = db.Column(db.Integer)
    hard_q = db.Column(db.Integer)
    score = db.Column(db.Integer)
    last_reviewed = db.Column(db.String)
