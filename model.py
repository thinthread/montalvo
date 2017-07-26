

from flask_sqlalchemy import SQLAlchemy
# update ... pip install flask-sqlalchemy

from sqlalchemy import func
# from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """User info."""
    # need to create user type: admin, teacher, studenty

    __tablename__ = "users"

    user_id_email = db.Column(db.String(20), primary_key=True)
    first_name = db.Column(db.String(15), nullable=False)
    last_name = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<User user_id_email=%s first_name=%s last_name=%s >" % \
                                                (self.user_id_email,
                                                 self.first_name,
                                                 self.last_name)


class Form(db.Model):
    """Details of forms and kinds of forms info."""
    # Need to change to handle BLOB forms or, Binary large objects instead of text

    __tablename__ = "forms"

    form_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    form_title = db.Column(db.String(30))
    last_time = db.Column(db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    def get_url(self):
        return "/forms/%s" % self.form_id

    def __repr__(self):
        return "<Form form_title=%s>" % (self.form_id,
                                                                     self.form_title)


class EventLog(db.Model):
    """Track user input events per create or update of a post."""

    __tablename__ = "event"

    event_log_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    last_time = db.Column(db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    user_id_email = db.Column(db.String(20), db.ForeignKey("users.user_id_email"))
    form_id = db.Column(db.Integer, db.ForeignKey("pens.s_pen_id"), index=True)

    user = db.relationship("User", backref=db.backref("events"))

    pen = db.relationship("Form", backref=db.backref("events"))

    def __repr__(self):
        return "<EventLog last_time=%s user_id_email=%s form_id=%s>" % (self.last_time,
                                                                         self.user_id_email,
                                                                         self.form_id)


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///montalvo_db'
    ## app.config['SQLALCHEMY_ECHO'] = False
    ## app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)

    db.create_all()

    print "Connected to DB."
