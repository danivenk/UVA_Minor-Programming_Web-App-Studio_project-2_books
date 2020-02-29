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

app.secret_key = os.urandom(16)


def none():
    # username = "testuser"
    # password = security.hash_psswd("test123")
    # name = "テスト"
    # db.execute("CREATE TABLE accounts (id SERIAL PRIMARY KEY, "
    #            "username VARCHAR NOT NULL, password VARCHAR NOT NULL, "
    #            "name VARCHAR NOT NULL);")
    # db.execute("INSERT INTO accounts (username, password, name) "
    #            "VALUES (:username, :password, :name)",
    #            {"username": username, "password": password, "name": name})
    # db.commit()
    pass


@app.route("/")
def index():

    if "username" in session:
        user = session.get("name")
        return render_template("index.html", login=True, user=user)
    else:
        return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    # get values from submitted form
    username = request.form.get("username")
    password = request.form.get("password")
    user = db.execute("SELECT password FROM accounts "
                      "WHERE username=:username",
                      {"username": username}).fetchall()

    # make sure the required values are given else give 400 error
    if not username or not password:
        abort(400, "No username/password specified")
    print(len(user))
    if len(user) != 1:
        abort(401, "Login failed")
        return redirect("/", 307)

    login_validity = security.compare_hash(user[0].password, password)

    if login_validity is True:
        session["username"] = username
    else:
        abort(401, "Login failed")

    return redirect("/", code=303)


@app.route("/logout")
def logout():
    session.pop("username", None)

    return redirect("/", code=303)


@app.errorhandler(HTTPException)
def errorhandler(error):
    """
    Handle errors

    used same code as in the exercise similarities

    return error template
    """
    error_message = str(error).split(":")
    return render_template("error.html", header=error_message[0],
                           message=error_message[1]), error.code


# https://github.com/pallets/flask/pull/2314
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
