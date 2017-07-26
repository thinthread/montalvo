from jinja2 import StrictUndefined

# import os
from flask import Flask, request, redirect  # ,url_for


from flask import send_from_directory
from flask_sse import sse
from flask_debugtoolbar import DebugToolbarExtension
from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from flask import Flask, Request

from model import (User, Form, EventLog, connect_to_db, db)

# import uuid   # for random file name uploads
# import json
# from model import connect_to_db, db
from sqlalchemy import or_
from sqlalchemy import func
from sqlalchemy import distinct

# import gcs_client
# from google.cloud import storage
# create cloud storage for BLOBs or PDF forms

#########from selenium import webdriver

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config["REDIS_URL"] = "redis://localhost"

app.register_blueprint(sse, url_prefix='/stream')


app.jinja_env.undefined = StrictUndefined
app.debug = True
app.jinja_env.auto_reload = app.debug  
# make sure templates, etc. are not cached in debug mode

# # Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

connect_to_db(app)



########################### VIEWS ###############################


@app.route("/", methods=["GET", "POST"])
def index():
    """Homepage."""

    if index:
        return render_template("homepage.html")


@app.route("/register_form")
def display_register_form():
    """Display register form"""

    return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register():
    """Register user"""

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")

    if db.session.query(User.user_id_email).filter_by(user_id_email=email).first():
        flash("Sorry the email has already been registered.")
        return redirect("/login_form")

    else:
        new_user = User(first_name=first_name,
                        last_name=last_name,
                        user_id_email=email,
                        password=password)

        db.session.add(new_user)
        db.session.commit()
        flash("You are successfully registered!")
        return render_template("homepage.html")


@app.route("/login_form", methods=["GET"])
def display_login_form():
    """Display login form"""

    return render_template("login_form.html")


@app.route("/login", methods=["POST"])
def login():
    """Login and display appropriate message"""

    email = request.form.get("email")
    password = request.form.get("password")
    print '\n\n\n email: ', email
    print '\n\n\n password: ', password
    user_info = User.query.filter_by(user_id_email=email).first()
    print '\n\n\n\n\n', user_info, '\n\n\n\n\n\n'
    if user_info:
        # user_id = user_info.user_id_email
        if user_info.password == password:
            flash("Successfully logged in!")
            session["login"] = user_info.user_id_email
            return redirect("/")

        else:
            flash("Wrong Password")
            return render_template("login_form.html")
    else:
        flash("User not found!")
        return render_template("login_form.html")


@app.route("/logout", methods=["GET"])
def logout_screen():
    """Display logout from form"""

    return render_template("logout.html")


@app.route("/logout", methods=["POST"])
def logout():
    """Display logout screen"""

    if session.get("login"):
        session.pop("login")

    flash("You have been successfully logged out.")

    return redirect("/")

# UPLOAD_FOLDER = '/path/to/the/uploads'
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# disallow .php files if the server executes them, but who has PHP installed on their server


@app.route("/create_form_post", methods=["POST", "GET"])
def create_form_post():
    """Create new form post, upload PDFs"""
    # need to handle BLOB, see google cloud storage for storing binary large objects like PDFs

    login = session.get('login')

    form_title = request.form.get("form_title")

    if form_name:

        form = db.session.query(Form.form_title).filter_by(form_title=form_name).first()

        if form:
                flash("Sorry that specific form name has already been created. \
                       Please choose another another. Thank you!")

                return redirect("/upload_form_post")

        elif form_name is None:

            flash("Sorry , you must fill out a form name/title on this post. Thank you!")
            return redirect("/upload_form_post")

        else:


            form_title = request.form.get("brand_name")


            new_form_post = Form(form_title=form_name)

            db.session.add(new_form_post)



            db.session.flush()

            new_user = login

            new_event = EventLog(user_id_email=new_user, form_id=new_form_post.form_id)

            db.session.add(new_event)
            db.session.commit()

            sse.publish({"id": new_form_post.form_id,
                         "form_name": form_name,
                         "name": form_name}, type='edit')

            flash("You have successfully created a new form post!")
            return redirect("/formsa/%s" % new_form_post.form_id)

    else:

        return render_template("create_form_pos.html", login=login)



@app.route("/forms/<int:form_id>", methods=["GET"])
def form(form_id):
    """Render single form, show detail."""

    form = Form.query.get(form_id)

    emails = [x.user_id_email for x in form.events]

    return render_template("form.html", form=form, contributors=set(emails))


@app.route("/last_modified", methods=["GET"])
def last_modified():

    forms = Form.query.order_by(Form.last_time.desc()).limit(5)

    nameurl = []
    for form in forms:
        nameurl.append({"name": form.form_title,
                        "id": form.form_id})

    return jsonify(nameurl)


@app.route("/show_search_results", methods=["GET"])
def show_search_results():
    """Search and retrieve data for user to see post"""

    search = request.args.get("brand_name").lower()  # manufacturer
    session["search"] = search

    forms = Form.query.filter(_or(func.lower(StockPen.form_title).contains(search))).all()

    return render_template("show_search_results.html", forms=forms)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.run(port=5001, host='0.0.0.0')

# if running gunicorn server , else just run server.py 
# gunicorn server:app --worker-class gevent --bind 0.0.0.0:5000 --reload --graceful-timeout 3
# WSGI web server gateway interface