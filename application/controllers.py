import os
from flask import Flask, request, redirect, url_for
from flask import render_template
from flask import current_app as app
from flask import session

import requests
import re
import statistics as st
import datetime


from application.database import db
from application.models import Card, User
from application.models import Deck
from flask import request

from sqlalchemy import and_

# For the session
app.secret_key = os.environ.get['APP_SESSION_KEY']

base_url = 'https://brainstorm-flashcard-app.herokuapp.com'

# ~ SIGN UP, LOG IN, etc


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/create-account", methods=["GET", "POST"])
def create_account():
    if request.method == "GET":
        return render_template("create_account.html")
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        valid_username = re.search("^[a-zA-Z0-9_]+$", username)
        if valid_username is not None:
            # pwd = "{}".format(password).encode("utf-8")
            # encoded = base64.b64encode(pwd)
            url = base_url + '/api/user'
            r = requests.post(
                url, data={'username': username, 'password': password})
            return redirect(url_for('login'))
        else:
            createAccountURL = url_for('create_account')
            return render_template("error.html", errorMessage="Username can not contain any special characters except an underscore. Yeah, we don't want any gamer nicknames here. I beg you 😅", goBack=createAccountURL)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get('user_id') == True:
            dashboardURL = url_for('dashboard')
            return render_template("error.html", errorMessage="Already logged in. Try this game, it would surely improve your memory 😁 ", goBack=dashboardURL)
        else:
            return render_template("login.html")

    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user_exists = db.session.query(User).filter(
            and_(User.username == username), (User.password == password)).first()
        if user_exists:
            user_id = User.query.filter(
                User.username == username).first().user_id
            session['user_id'] = user_id
            session['username'] = request.form['username']
            return redirect(url_for('dashboard'))
        else:
            loginURL = url_for('login')
            return render_template("error.html", errorMessage="Invalid credentials. Think harder. You'll get it. You have to. There isn't a 'forgot password' feature yet 😌", goBack=loginURL)
    else:
        return render_template("error.html", errorMessage="Error. I have to look into it. Seriously. Just try again with a different URL. Please don't come back here until this error vanishes 🙏")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if 'username' in session:
        user_id = session['user_id']
        username = session['username']
        url = base_url + '/api/deck'
        decks = requests.get(url, {"user_id": user_id}).json()
        reviews = []
        if len(decks) > 1:
            for deck in decks:
                deck_id = deck["deck_id"]
                url = base_url + "/api/review/{}".format(deck_id)
                review = requests.get(url).json()
                reviews.append(review)

            scores = []
            maxScore = -1
            minScore = 100
            hardestDeck = ''
            easiestDeck = ''

            for index, review in enumerate(reviews):
                scores.append(review['score'])
                if review['score'] >= maxScore:
                    maxScore = review['score']
                    easiestDeck = decks[index]['deck_name']
                if review['score'] <= minScore:
                    minScore = review['score']
                    hardestDeck = decks[index]['deck_name']

            avgScore = round(st.mean(scores), 2)
            stdevScore = round(st.stdev(scores), 2)
            revisionRequired = []
            for index, review in enumerate(reviews):
                if review['score'] < avgScore:
                    revisionRequired.append(decks[index]['deck_name'])

            return render_template("dashboard.html", decks=decks, reviews=reviews, username=username, avgScore=avgScore, stdevScore=stdevScore, easiestDeck=easiestDeck, hardestDeck=hardestDeck, revisionRequired=revisionRequired)
        else:
            for deck in decks:
                deck_id = deck["deck_id"]
                url = base_url + "/api/review/{}".format(deck_id)
                review = requests.get(url).json()
                reviews.append(review)
            return render_template("dashboard.html", decks=decks, reviews=reviews, username=username, avgScore="-", stdevScore="-", easiestDeck="-", hardestDeck="-", revisionRequired="-")

    else:
        loginURL = url_for('login')
        return render_template("error.html", errorMessage="You are not logged in ! Try logging in again. You can do it this time 💪", goBack=loginURL)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))


# ~ DECK MANAGEMENT

@app.route("/deck-management", methods=["GET", "POST"])
def deck_management():
    return render_template("deck_management.html")


@app.route("/deck-management/add", methods=["GET", "POST"])
def add_deck():
    if request.method == "GET":
        return render_template("add_deck.html")
    elif request.method == "POST":
        resp = request.form
        deck_name = resp["deck_name"]
        no_of_questions = resp["QACount"]
        user_id = session["user_id"]
        questions = []
        answers = []
        addDeckURL = url_for('add_deck')
        if len(deck_name) > 1 and len(deck_name) <= 20:
            if int(no_of_questions) <= 5:
                for i in range(1, int(no_of_questions)+1):
                    question = 'q' + str(i)
                    answer = 'a' + str(i)
                    if resp[question] != "":
                        questions.append(resp[question])
                    else:
                        return render_template("error.html", errorMessage="One or more questions are empty. Please fill out all the questions. I mean you would atleast like to know the questions right 😆?", goBack=addDeckURL)
                    if resp[answer] != "":
                        answers.append(resp[answer])
                    else:
                        return render_template("error.html", errorMessage="One or more answers are empty. Please fill out all the answers. That way you can check them while playing. Just restrain yourself from cheating 😉", goBack=addDeckURL)

                # - Add the deck
                url = base_url + '/api/deck/'
                r = requests.post(
                    url, data={'deck_name': deck_name, 'user_id': user_id})

                # - Add the cards. For this we need the deck_id.
                deck = Deck.query.filter(
                    and_(Deck.deck_name == deck_name), (Deck.user_id == user_id)).first()
                url = base_url + '/api/card/'
                r = requests.post(
                    url, data={'questions': questions, 'answers': answers, 'deck_id': deck.deck_id})

                url = base_url + "/api/review/{}".format(deck.deck_id)
                x = datetime.datetime.now()
                date = x.strftime("%x")
                results = {
                    "total_q": 0,
                    "easy_q": 0,
                    "medium_q": 0,
                    "hard_q": 0,
                    "score": 0,
                    "last_reviewed": date,
                }

                r = requests.post(url, json=results)
                return redirect(url_for('dashboard'))
            else:
                dashboardURL = url_for("dashboard")
                return render_template("error.html", errorMessage="Too many card. Please give atmost 5 cards per deck. 😀", goBack=dashboardURL)
        else:
            dashboardURL = url_for("dashboard")
            return render_template("error.html", errorMessage="Name too small or too big. Please give a name that is atleast 2 and atmost 20 characters long. Go on. 😀", goBack=dashboardURL)


@app.route("/deck-management/edit", methods=["GET", "PUT", "POST"])
def edit_deck():
    if request.method == "GET":
        deck_id = request.args.get('deck_id')
        deck = db.session.query(Deck).filter(
            Deck.deck_id == deck_id).first()
        return render_template("edit_deck.html", deck=deck)
    elif request.method == "POST":
        new_name = request.form['deck_name']
        deck_id = request.args.get('deck_id')
        deck = db.session.query(Deck).filter(
            Deck.deck_id == deck_id).first()
        if deck.deck_name != new_name:
            if len(new_name) > 1 and len(new_name) <= 20:
                url = base_url + "/api/deck/"
                r = requests.put(
                    url, data={'deck_id': deck_id, 'deck_name': new_name})
                return redirect(url_for("dashboard"))
            else:
                dashboardURL = url_for("dashboard")
                return render_template("error.html", errorMessage="Name too small or too big. Please give a name that is atleast 2 and atmost 20 characters long. Go on. 😀", goBack=dashboardURL)
        else:
            dashboardURL = url_for("dashboard")
            return render_template("error.html", errorMessage="Deck has the same name. Lost in thought huh ? Play this game often. It will improve your memory 😃", goBack=dashboardURL)


@app.route("/deck-management/delete", methods=["GET", "POST", "DELETE", "OPTIONS"])
def delete():
    if request.method == "GET":
        deck_id = request.args.get('deck_id')
        card_id = request.args.get('card_id')
        if deck_id:
            deck = db.session.query(Deck).filter(
                Deck.deck_id == deck_id).first()
            return render_template("delete_modal.html", deck=deck, card_id=None)
        if card_id:
            return render_template("delete_modal.html", card_id=card_id, deck=None)
    elif request.method == "POST":
        deck_id = request.args.get('deck_id')
        card_id = request.args.get('card_id')
        if deck_id:
            deck = db.session.query(Deck).filter(
                Deck.deck_id == deck_id).first()
            deck_name = deck.deck_name

            entered_name = request.form['confirm_deletion']
            if entered_name == deck_name:
                # 1. Delete all the cards related to that deck
                cards = db.session.query(Card).filter(
                    Card.deck_id == deck_id).delete(synchronize_session=False)
                db.session.commit()

                # 2. Delete the review
                url = base_url + "/api/review/{}".format(deck_id)
                r = requests.delete(url)

                # 3. Delete the deck
                url = base_url + "/api/deck/{}".format(deck_id)
                r = requests.delete(url)

                return redirect(url_for('dashboard'))
            else:
                return render_template(
                    "error.html", errorMessage="Incorrect deck name. Come on ! I wrote that in bold 😑")
        if card_id:
            entered_id = request.form['confirm_deletion']
            if entered_id == card_id:
                cards = db.session.query(Card).filter(
                    Card.card_id == card_id).delete(synchronize_session=False)
                db.session.commit()
                return redirect(url_for('dashboard'))
            else:
                return render_template(
                    "error.html", errorMessage="Incorrect card id. Come on ! I wrote that in bold 😑")
        else:
            return render_template("error.html", errorMessage="Invalid endpoint. Yeahhh, how did you get here though ? Even I couldn't get here 🤔")


@app.route("/deck-management/cards", methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"])
def edit_cards():
    if request.method == "GET":
        deck_id = request.args.get("deck_id")
        url = base_url + "/api/card/{}".format(deck_id)
        cards = requests.get(url).json()
        add_new_card = request.args.get('addCard')
        if add_new_card:
            return render_template("edit_cards.html", cards=cards, deck_id=deck_id, add_new_card=add_new_card)
        else:
            return render_template("edit_cards.html", cards=cards, deck_id=deck_id, add_new_card=add_new_card)

    elif request.method == "POST":
        deck_id = request.args.get("deck_id")
        add_new_card = request.args.get('addCard')
        if add_new_card:
            new_question = request.form['q_edited']
            new_answer = request.form['a_edited']
            url = base_url + "/api/card/"
            r = requests.post(url, data={
                              'questions': new_question, 'answers': new_answer, 'deck_id': deck_id})
            return redirect(url_for('edit_cards', deck_id=deck_id, addCard=True))
        else:
            new_question = request.form['q_edited']
            new_answer = request.form['a_edited']
            card_id = request.form['submit']
            card = db.session.query(Card).filter(
                Card.card_id == card_id).first()
            old_question = card.question
            old_answer = card.answer
            if((old_answer != new_answer) or (old_question != new_question)):
                url = base_url + "/api/card/"
                r = requests.put(url, data={
                                 'card_id': card_id, 'question': new_question, 'answer': new_answer})
                return redirect(url_for('edit_cards', deck_id=deck_id))
            else:
                return redirect(url_for('edit_cards', deck_id=deck_id))


# ~ REVIEW and SCORING

@app.route("/play", methods=["GET", "PUT", "POST"])
def play():
    if request.method == "GET":
        return render_template("play.html")

    elif request.method == "POST":
        return "card"
    else:
        return ""
