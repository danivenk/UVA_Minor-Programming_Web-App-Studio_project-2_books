import os

from flask import Flask, session, render_template, request, abort, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException
from functions import security

app = Flask(__name__)

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
            forbidden = ["log", "static", "register"]
            login_req = ["search"]

            # exlcude items in forbidden
            if any(item in endpoint for item in forbidden):
                pass

            # add index as "Home"
            elif "index" in endpoint:
                url_list[endpoint] = ["Home", None]

            # add items where login is required
            elif any(item in endpoint for item in login_req):
                url_list[endpoint] = [endpoint.capitalize(), True]

            # add items the rest
            else:
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
        - request is anything else than a "GET" request

    returns the homepage with parameters if logged on
    """

    url_list = session.get("urls")

    # check if request is a "GET" request
    if request.method == "GET":

        # check if someone is logged on
        if "username" in session:

            # get username if so and render
            user = session.get("username")

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
        - request is anything else than "POST" or "GET"

    returns the register form again if the retype password and password
        weren't the same or the request was a "GET" request. If registration
        was successfull it redirects (303) to "/".
    """

    url_list = session.get("urls")

    # check if request was a "POST" or a "GET" request
    if request.method == "POST":

        # get all values from the submitted form
        username = request.form.get("register_username")
        password = request.form.get("register_password")
        rpassword = request.form.get("register_rpassword")

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
        - method is anthing else than POST

    returns a redirect (303) to "/"

    used session for loggin in and out as in:
        https://flask.palletsprojects.com/en/1.1.x/quickstart/#sessions
    """

    # check if request is a "POST" request
    if request.method == "POST":

        # get values from submitted form
        username = request.form.get("username")
        password = request.form.get("password")

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

        return redirect("/", code=303)

    # abort using a 405 HTTPException
    abort(405)


@app.route("/logout", methods=["GET"])
def logout():
    """
    logs out

    aborts if:
        - method is anything else than GET

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

    url_list = session.get("urls")

    # check if request is a "GET" request
    if request.method == "GET":

        # check if someone is logged on
        if "username" in session:

            # get username if so and render
            user = session.get("username")

            return render_template("index.html", login=True, user=user,
                                   urls=url_list)
        else:

            abort(403)

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

    # split the error into the header and message
    error_message = str(error).split(":")

    return render_template("error.html", header=error_message[0],
                           message=error_message[1]), error.code


# https://github.com/pallets/flask/pull/2314
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
