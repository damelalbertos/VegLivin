from app import app, db
from app.models import User, UserToEvent, Friends, Post, Notification, Event


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'UserToEvent': UserToEvent, 'Friends': Friends,
            'Post': Post, 'Notification': Notification, 'Event': Event}
