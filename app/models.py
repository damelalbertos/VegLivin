from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    dob = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    user_details = db.Column(db.String(150))
    events = db.relationship('UserToEvent', back_populates='user', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_details = db.Column(db.String(150))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    likes = db.Column(db.Integer)
    comments = db.Column(db.Integer)
    favorites = db.Column(db.Integer)

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String)
    title = db.Column(db.String(64))
    start_time_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    organizer = db.Column(db.Integer, db.ForeignKey('user.id'))
    attendees = db.relationship("UserToEvent", back_populates='event', lazy=True)

    def __repr__(self):
        return '<Event {}>'.format(self.title)


class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Friends {}>'.format(self.id)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    type = db.Column(db.String(64))

    def __repr__(self):
        return '<Notifications {}>'.format(self.id)


class UserToEvent(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    extra_data = db.Column(db.String(50))
    event = db.relationship("Event", back_populates="attendees")
    user = db.relationship("User", back_populates="events")

    def __repr__(self):
        return '<UserToEvent {}>'.format(self.id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
