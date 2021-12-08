from operator import and_
import re
from flask import request
from flask_restful import Resource
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from application.database import db
from application.models import Deck, Review, User, Card
from application.validation import BusinessValidationError

# ~ VARIOUS PARSERS

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username')
create_user_parser.add_argument('password')

create_deck_parser = reqparse.RequestParser()
create_deck_parser.add_argument('deck_name')
create_deck_parser.add_argument('user_id')

get_deck_parser = reqparse.RequestParser()
get_deck_parser.add_argument('user_id')

put_deck_parser = reqparse.RequestParser()
put_deck_parser.add_argument('deck_id')
put_deck_parser.add_argument('deck_name')

create_card_parser = reqparse.RequestParser()
create_card_parser.add_argument('questions', action='append')
create_card_parser.add_argument('answers', action='append')
create_card_parser.add_argument('deck_id')

get_card_parser = reqparse.RequestParser()
get_card_parser.add_argument('deck_id')

put_card_parser = reqparse.RequestParser()
put_card_parser.add_argument('card_id')
put_card_parser.add_argument('question')
put_card_parser.add_argument('answer')

# ~ FOR MARSHAL-WITH OUTPUT

card_output_fields = {
    "deck_id": fields.Integer,
    "card_id": fields.Integer,
    "question": fields.String,
    "answer": fields.String
}

review_output_fields = {
    "total_q": fields.Integer,
    "easy_q": fields.Integer,
    "medium_q": fields.Integer,
    "hard_q": fields.Integer,
    "score": fields.Integer,
    "last_reviewed": fields.String
}

deck_output_fields = {
    "deck_id": fields.Integer,
    "deck_name": fields.String
}

# _ User API


class UserAPI(Resource):
    def post(self):
        args = create_user_parser.parse_args()
        username = args.get("username", None)
        password = args.get("password", None)
        if username is None:
            raise BusinessValidationError(
                status_code=400, error_message="Username is required")
        if password is None:
            raise BusinessValidationError(
                status_code=400, error_message="Password is required")

        user = db.session.query(User).filter(User.username == username).first()
        if user:
            raise BusinessValidationError(
                status_code=400, error_message="Duplicate user")

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return "NEW USER CREATED"

# _ Deck API


class DeckAPI(Resource):

    @marshal_with(deck_output_fields)
    def get(self):
        args = get_deck_parser.parse_args()
        user_id = args.get("user_id", None)
        if user_id is None:
            raise BusinessValidationError(
                status_code=404, error_message="User does not exist")
        deck = db.session.query(Deck).filter(Deck.user_id == user_id).all()
        return deck

    @marshal_with(deck_output_fields)
    def put(self):
        args = put_deck_parser.parse_args()
        deck_id = args.get('deck_id', None)
        new_name = args.get('deck_name', None)
        if deck_id is None:
            raise BusinessValidationError(
                status_code=400, error_message="deck_id is required")
        deck = db.session.query(Deck).filter(Deck.deck_id == deck_id).first()
        deck.deck_name = new_name
        db.session.add(deck)
        db.session.commit()
        return deck

    def post(self):
        args = create_deck_parser.parse_args()
        deck_name = args.get("deck_name", None)
        user_id = args.get("user_id", None)
        if deck_name is None:
            raise BusinessValidationError(
                status_code=400, error_message="Deck name is required")
        if user_id is None:
            raise BusinessValidationError(
                status_code=400, error_message="User id is required")

        new_deck = Deck(deck_name=deck_name, user_id=user_id)
        db.session.add(new_deck)
        db.session.commit()
        return "NEW DECK CREATED"

    def delete(self, deck_id):
        deck = db.session.query(Deck).filter(
            Deck.deck_id == deck_id).delete(synchronize_session=False)
        db.session.commit()
        return "DECK DELETED"

# _ Card API


class CardAPI(Resource):

    @marshal_with(card_output_fields)
    def get(self, deck_id):
        cards = db.session.query(Card).filter(Card.deck_id == deck_id).all()
        return cards

    def post(self):
        args = create_card_parser.parse_args()
        questions = args['questions']
        answers = args['answers']
        deck_id = args.get("deck_id", None)

        if questions is None:
            raise BusinessValidationError(
                status_code=400, error_message="Questions are required")
        if answers is None:
            raise BusinessValidationError(
                status_code=400, error_message="Answers are required")

        # print(questions, type(questions), len(questions))
        for i in range(0, len(questions)):
            new_card = Card(
                question=questions[i], answer=answers[i], deck_id=deck_id)
            db.session.add(new_card)
            db.session.commit()

        return "NEW CARD CREATED"

    @marshal_with(card_output_fields)
    def put(self):
        args = put_card_parser.parse_args()
        card_id = args.get('card_id', None)
        new_question = args.get('question', None)
        new_answer = args.get('answer', None)

        card = db.session.query(Card).filter(Card.card_id == card_id).first()
        card.question = new_question
        card.answer = new_answer
        db.session.add(card)
        db.session.commit()
        return card

    def delete(self, card_id):
        card = db.session.query(Card).filter(
            Card.card_id == card_id).delete(synchronize_session=False)
        db.session.commit()
        return "DELETED"


# _ Review API

class ReviewAPI(Resource):

    @marshal_with(review_output_fields)
    def get(self, deck_id):
        review = db.session.query(Review).filter(
            Review.deck_id == deck_id).first()
        return review

    @marshal_with(review_output_fields)
    def put(self, deck_id):
        data = request.get_json()
        new_total_q = data['total_q']
        new_easy_q = data['easy_q']
        new_medium_q = data['medium_q']
        new_hard_q = data['hard_q']
        new_score = data['score']
        new_last_reviewed = data['last_reviewed']

        review = db.session.query(Review).filter(
            Review.deck_id == deck_id).first()

        review.total_q = new_total_q
        review.easy_q = new_easy_q
        review.medium_q = new_medium_q
        review.hard_q = new_hard_q
        review.score = new_score
        review.last_reviewed = new_last_reviewed

        db.session.add(review)
        db.session.commit()
        return review

    def post(self, deck_id):
        data = request.get_json()
        total_q = data['total_q']
        easy_q = data['easy_q']
        medium_q = data['medium_q']
        hard_q = data['hard_q']
        score = data['score']
        last_reviewed = data['last_reviewed']
        if total_q is None:
            raise BusinessValidationError(
                status_code=400, error_message="Total questions are required")
        if easy_q is None:
            raise BusinessValidationError(
                status_code=400, error_message="Number of easy questions are required")

        if medium_q is None:
            raise BusinessValidationError(
                status_code=400, error_message="Number of medium questions are required")

        if hard_q is None:
            raise BusinessValidationError(
                status_code=400, error_message="Number of hard questions are required")

        if score is None:
            raise BusinessValidationError(
                status_code=400, error_message="Score is required")

        if last_reviewed is None:
            raise BusinessValidationError(
                status_code=400, error_message="Last reviewed is required")

        new_review = Review(deck_id=deck_id, total_q=total_q, easy_q=easy_q, medium_q=medium_q,
                            hard_q=hard_q, score=score, last_reviewed=last_reviewed)
        db.session.add(new_review)
        db.session.commit()
        return "NEW REVIEW ADDED"

    def delete(self, deck_id):
        review = db.session.query(Review).filter(
            Review.deck_id == deck_id).delete(synchronize_session=False)
        db.session.commit()
        return "REVIEW DELETED"
