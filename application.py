#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
version: python 3+
application.py defines the flask app
Dani van Enk, 11823526

references:
    https://cs50.harvard.edu/web/notes/3/
"""

# used imports
import os
import requests
import json
import re

from flask import Flask, session, render_template, request, abort, redirect, \
                  jsonify, escape
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException
from functions import security

# create flask app
app = Flask(__name__)

# make sure the json keys aren't sorted
app.config['JSON_SORT_KEYS'] = False

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# create a secret_key
app.secret_key = os.urandom(16)


@app.before_request
def setup_urls():
    """
    create a dictionary for the navbar items
    """

    # get all routes in the app
    urls = app.url_map.iter_rules()

    # create an empty dictionary
    url_list = dict()

    # iterate over all routes in the app
    for url in urls:

        # filter for routes with a "GET" method
        if "GET" in url.get_empty_kwargs()["methods"]:

            # get the endpoint of the route
            endpoint = url.get_empty_kwargs()["endpoint"]

            # define the routes excluded and only available if logged on
            forbidden = ["log", "static", "register", "api", "book"]
            login_req = ["search"]

            # check if allowed
            allowed = not any(item in endpoint for item in forbidden)

            # add index as "Home"
            if "index" in endpoint and allowed:
                url_list[endpoint] = ["Home", None]

            # add items where login is required
            elif any(item in endpoint for item in login_req) and allowed:
                url_list[endpoint] = [endpoint.capitalize(), True]

            # add items the rest
            elif allowed:
                url_list[endpoint] = [endpoint.capitalize(), None]

    # sort dictionary by key
    url_list = dict(sorted(url_list.items(), key=lambda x: x[0]))

    # add url_list to session
    session["urls"] = url_list


@app.route("/", methods=["GET"])
def index():
    """
    renders the homepage

    aborts if:
        - request is anything else than a "GET" request (405)

    returns the homepage with parameters if logged on
    """

    url_list = session.get("urls")

    # check if someone is logged on
    if "username" in session:

        # get username if so and render
        user = session.get("username")

    # check if request is a "GET" request
    if request.method == "GET":
        if user:
            return render_template("index.html", login=True, user=user,
                                   urls=url_list)
        else:
            return render_template("index.html", urls=url_list)

    # abort using a 405 HTTPException
    abort(405)


@app.route("/register", methods=["POST", "GET"])
def register():
    """
    register a new user

    aborts if:
        - no username/password/retype password is given (400)
        - user already registered (400)
        - request is anything else than "POST" or "GET" (405)

    returns the register form again if the retype password and password
        weren't the same or the request was a "GET" request. If registration
        was successfull it redirects (303) to "/".
    """

    url_list = session.get("urls")

    # check if request was a "POST" or a "GET" request
    if request.method == "POST":

        # get all values from the submitted form
        username = escape(request.form.get("register_username"))
        password = escape(request.form.get("register_password"))
        rpassword = escape(request.form.get("register_rpassword"))

        # if the given passwords aren't the same rerender the template
        if password != rpassword:
            return render_template("register.html", message="passwords weren't"
                                   " the same...", urls=url_list)

        # if no username/password/retype password were given abort (400)
        if not username or not password or not rpassword:

            # abort using a 400 HTTPException
            abort(400, "No username/password specified")

        # search database for user
        user = db.execute("SELECT * FROM accounts "
                          "WHERE username=:username",
                          {"username": username}).fetchall()

        # if username was found in the database abort (400)
        if len(user) >= 1:

            # abort using a 400 HTTPException
            abort(400, "User already registered")

        # hash password
        password = security.hash_psswd(password)

        # add username and password to database and commit
        db.execute("INSERT INTO accounts (username, password) "
                   "VALUES (:username, :password)",
                   {"username": username, "password": password})
        db.commit()

        return redirect("/", 303)

    elif request.method == "GET":

        return render_template("register.html", urls=url_list)

    # abort using a 405 HTTPException
    abort(405)


@app.route("/login", methods=["POST"])
def login():
    """
    logs on using the user posted login details

    aborts if:
        - no username/password is specified (400)
        - the database gives more or less than 1 account back (401)
        - the credentials are invalid (401)
        - method is anthing else than POST (405)

    returns a redirect (303) to "/"

    used session for loggin in and out as in:
        https://flask.palletsprojects.com/en/1.1.x/quickstart/#sessions
    """

    # check if request is a "POST" request
    if request.method == "POST":

        # get values from submitted form
        username = escape(request.form.get("username"))
        password = escape(request.form.get("password"))

        # find user in database
        user = db.execute("SELECT password FROM accounts "
                          "WHERE username=:username",
                          {"username": username}).fetchall()

        # make sure the required values are given else give 400 error
        if not username or not password:

            # abort using a 400 HTTPException
            abort(400, "No username/password specified")

        # check if the username returns more or less 1 user in database
        if len(user) != 1:

            # abort using a 401 HTTPException
            abort(401, "Login failed")
            return redirect("/", 303)

        # check if the given password matches the one from the databes
        login_validity = security.compare_hash(user[0].password, password)

        # if it is the same as in the database add username to the session
        if login_validity is True:
            session["username"] = username
        else:

            # abort using a 401 HTTPException
            abort(401, "Login failed")

        return redirect("/search", code=303)

    # abort using a 405 HTTPException
    abort(405)


@app.route("/logout", methods=["GET"])
def logout():
    """
    logs out

    aborts if:
        - method is anything else than GET (405)

    returns a redirect (303) to "/"

    used session for loggin in and out as in:
        https://flask.palletsprojects.com/en/1.1.x/quickstart/#sessions
    """

    # check if request is a "GET" request
    if request.method == "GET":

        # remove username from session
        session.pop("username", None)

        return redirect("/", code=303)

    # abort using a 405 HTTPException
    abort(405)


@app.route("/search", methods=["GET"])
def search():
    """
    searches the query in the database and shows the result

    aborts if:
        - post is something else than a "GET" request (405)
        - if not logged on (403)

    it returns the search page
    """

    # get the url list from the session
    url_list = session.get("urls")

    # check if someone is logged on
    if "username" in session:

        # get username if so and render
        user = session.get("username")

    # check if request is a "GET" request and if user is logged on
    if request.method == "GET" and user:

        # get the search query
        search_query = str(request.args.get("search"))

        # split the query into single words (escape the query)
        search = re.split(r'\W+', search_query)

        # predefine an empty list for the results
        results = []

        # search each word in the database
        for query in search:

            # exclude any escaped words
            if query:

                # search in the columns of the book database for the query
                db_res = db.execute("SELECT * FROM books WHERE (title ILIKE "
                                    f"'%{query}%' or author ILIKE '%{query}%'"
                                    f" or isbn ILIKE '%{query}%')").fetchall()

                # add all items to the result list
                for db_result in db_res:

                    # make sure noe doubles added to the results
                    if db_result not in results:
                        results.append(db_result)

        return render_template("search.html", login=True, user=user,
                               urls=url_list, search_query=search_query,
                               results=results)

    # abort if not logged on
    elif not user:
        abort(403)

    # abort using a 405 HTTPException
    abort(405)


@app.route("/<isbn>", methods=["GET", "POST"])
def book(isbn):

    url_list = session.get("urls")

    # check if someone is logged on
    if "username" in session:

        # get username if so and render
        user = session.get("username")

    # check if request is a "GET" request and user logged on
    if request.method == "GET" and user:

        # get books/reviews for this isbn and all users
        books = db.execute("SELECT * FROM books WHERE isbn=:isbn",
                           {"isbn": isbn}).fetchall()
        reviews = db.execute("SELECT * FROM reviews JOIN books ON "
                             "reviews.book_id = books.id WHERE isbn=:isbn",
                             {"isbn": isbn}).fetchall()
        users = db.execute("SELECT username FROM accounts").fetchall()

        # define url for the goodreads api with this isbn
        URL = "https://www.goodreads.com/book/review_counts.json?key=" \
            f"4cWZI3ifMz0RSj1NFaYiBQ&isbns={isbn}"

        # if there can be made a connection to the goodreads api get te values
        if requests.get(URL).status_code == 200:

            # get the goodreads api values
            gr_data = requests.get(URL)

            # convert the json data to dictionary
            data = json.loads(gr_data.text)

            # get the average_rating and ratings_count
            gr_ar = data["books"][0]["average_rating"]
            gr_nor = data["books"][0]["ratings_count"]

            # make a list with those values
            goodreads = [gr_ar, gr_nor]

            # if the rating or count is 0 give goodreads the value none instead
            if gr_ar == "0.0" or gr_nor == 0:
                goodreads = None

        # if no connection could be made, give goodreads a null value
        else:
            goodreads = None

        # if there are more than 1 book for the same isbn abort
        if len(books) > 1:
            abort(400)
        # 404 abort if none are found
        elif len(books) == 0:
            abort(404)

        # get first item in the books list (got list from database fetch)
        book = books[0]

        return render_template("book.html", book=book, reviews=reviews,
                               users=users, login=True, user=user,
                               urls=url_list, goodreads=goodreads)

    # if not logged on abort
    elif not user:
        abort(403)

    # check if request is a "POST" request
    elif request.method == "POST":

        # check if someone is logged on
        if "username" in session:

            # get username if so and render
            user_name = session.get("username")

            # get username/rating/review_text from the form
            username = escape(request.form.get("review_username"))
            rating = escape(request.form.get("rating"))
            review_text = escape(request.form.get("review"))

            # abort if review user is not logged on user
            if user_name != username:
                abort(403, "You can't submit a review which is not"
                      "under your name.")

            # look in database if user review is already present of this user
            user_check = db.execute("SELECT * FROM reviews WHERE user_id=("
                                    "SELECT id FROM accounts WHERE username="
                                    ":username) and book_id=(SELECT id FROM "
                                    "books WHERE isbn=:isbn)",
                                    {"username": username,
                                     "isbn": isbn}).fetchall()

            # abort user tries to review more then once on the same book
            if len(user_check) != 0:
                abort(403, "You can't review more than once.")

            # add review to database
            db.execute("INSERT INTO reviews (user_id, rating, text, book_id) "
                       "VALUES ((SELECT id from accounts where "
                       "username=:username), :rating, :text, (SELECT id from "
                       "books where isbn=:isbn))",
                       {"username": username, "rating": rating,
                        "text": review_text, "isbn": isbn})

            # update book after review has been submitted
            db.execute("UPDATE books SET (review_count, average_score)="
                       "(SELECT COUNT(*), AVG(rating) FROM reviews "
                       "WHERE book_id=(SELECT id FROM books WHERE isbn=:isbn))"
                       " WHERE isbn=:isbn", {"isbn": isbn})

            # commit to database
            db.commit()

            return redirect(f"/{isbn}", 303)

        # abort if not logged in
        abort(403)

    # abort using a 405 HTTPException
    abort(405)


@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):
    """
    creates the api for the web application

    aborts if:
        - the resquest is anything else than a "GET" request
        - somehow there are more than one entry of 1 isbn (401)
        - isbn not found in database (404)


    returns a json version of the book data
    """

    # check if request is a "GET" request
    if request.method == "GET":

        # get book with the isbn from the database
        books = db.execute("SELECT * FROM books WHERE isbn=:isbn",
                           {"isbn": isbn}).fetchall()

        # if there are more than 1 book for the same isbn abort
        if len(books) > 1:
            abort(401)
        # 404 abort if none are found
        elif len(books) == 0:
            abort(404)

        # get first item in the books list (got list from database fetch)
        book = books[0]

        # average_score must be a #.# type so used formatted string
        return jsonify(title=book.title, author=book.author, year=book.year,
                       isbn=book.isbn, review_count=book.review_count,
                       average_score=f"{book.average_score:.1f}")

    # abort using a 405 HTTPException
    abort(405)


@app.errorhandler(HTTPException)
def errorhandler(error):
    """
    Handle errors

    used same code as in the exercise similarities

    return error template

    reused part of the code from the Survey and Similarities web apps
        from UVA Mprog Programming 2 Module 10 - Web
    """

    # get url list from session
    url_list = session.get("urls")

    # split the error into the header and message (index, 0 header, 1 text)
    error_message = str(error).split(":")

    # check if someone is logged on
    if "username" in session:

        # get username if so and render
        user = session.get("username")

        return render_template("error.html", header=error_message[0],
                               message=error_message[1], login=True, user=user,
                               urls=url_list), error.code
    else:

        return render_template("error.html", header=error_message[0],
                               message=error_message[1], urls=url_list), \
                               error.code


# https://github.com/pallets/flask/pull/2314
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
