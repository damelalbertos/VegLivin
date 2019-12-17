from datetime import datetime
import os

from flask import render_template, flash, redirect, url_for, request, app, Flask
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, EventForm
from app.models import User, Event, UserToEvent, Post, Notification

app.config["IMAGE_UPLOADS"] = "/mnt/c/wsl/projects/pythonise/tutorials/flask_series/app/app/static/img/uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    return render_template('index.html', title='Home', form=form,
                           posts=posts.items)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        person = User(first_name=form.firstname.data, last_name=form.lastname.data, dob=form.dob.data,
                      email=form.email.data)
        person.set_password(form.password.data)
        db.session.add(person)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign up', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    if user is None:
        user = User.query.filter_by(username=username).first_or_404()
        db.session.commit(user)
        flash('Your changes have been saved.')
        return redirect(url_for('index'))
    else:
        flash('You cannot use that username')

    render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.user_details = form.v_Status.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.v_Status.data = current_user.user_details
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/new_event', methods=['GET', 'POST'])
def new_event():
    form = EventForm()
    if form.validate_on_submit():
        flash('New event requested for Event {}'.format(form.eventName.data))
        my_event = Event(eventName=form.eventName.data, dateTime=form.date.data, venue_id=form.venueName.data)
        db.session.add(my_event)
        db.session.commit()
    return render_template('new_event.html', title='New event', form=form)

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


def allowed_image(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):
    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False


@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":

        if request.files:

            if "filesize" in request.cookies:

                if not allowed_image_filesize(request.cookies["filesize"]):
                    print("Filesize exceeded maximum limit")
                    return redirect(request.url)

                image = request.files["image"]

                if image.filename == "":
                    print("No filename")
                    return redirect(request.url)

                if allowed_image(image.filename):
                    filename = secure_filename(image.filename)

                    image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))

                    print("Image saved")

                    return redirect(request.url)

                else:
                    print("That file extension is not allowed")
                    return redirect(request.url)

    return render_template("/upload_image.html")


@app.route('/Home', methods=['GET', 'POST'])
def home():
    pass
    return render_template('Home.html', title='Home')


@app.route('/reset_db')
def reset_db():
    # if current_user.is_authenticated:
    #     return redirect(url_for('reset_db'))
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()

    dt1 = datetime(1997, 1, 9)
    dt2 = datetime(1998, 1, 11)
    dt3 = datetime(2000, 4, 13)

    dt4 = datetime(2019, 10, 19)
    dt5 = datetime(2020, 10, 1)
    dt6 = datetime(2019, 4, 3)

    dt7 = datetime(2019, 12, 19)
    dt8 = datetime(2019, 12, 20)
    dt9 = datetime(2019, 12, 20)
    dt10 = datetime(2019, 12, 21)

    e1 = Event(eventName='Vegan Pop-Up', location='Brooklyn, Ny', organizer='Louis Garner', start_time_date=dt4)
    e2 = Event(eventName='Healthy Eating', location='Bronx, Ny', organizer='Tomas Jennings', start_time_date=dt5)
    e3 = Event(eventName='Plant-Based Plantluck', location='Ithaca, Ny', organizer='Tobey Winter', start_time_date=dt6)

    p1 = Post(post_details="I am looking for a vegan event for a kid", likes=5, comments=6, favorites=7)
    p2 = Post(post_details="I hosting this event about healthy eating, please check it out", likes=20, comments=0,
              favorites=1)
    p3 = Post(post_details="Hey I am new to the site and looking for friends", likes=100, comments=30, favorites=20)

    u1 = User( username='AmberV', email="Amber@gmail.com", dob=dt1, user_details='Vegan',
              posts=[p1])
    u2 = User( username='FrankHood', email="Frank@gmail.com",  dob=dt2, user_details='Flexitarian',
              posts=[p2])
    u3 = User( username='HealthyFood', email="Manon@gmail.com", dob=dt3, user_details='Vegetarian',
              posts=[p3])

    u2e1 = UserToEvent(user=u1, event=e1)
    u2e2 = UserToEvent(user=u1, event=e2)
    u2e3 = UserToEvent(user=u2, event=e1)
    u2e4 = UserToEvent(user=u3, event=e3)

    db.session.add_all([u1, u2, u3, e1, e2, e3, p1, p2, p3, u2e1, u2e2, u2e3, u2e4])
    db.session.commit()

    n1 = Notification(recipient_id=u1.id, sender_id=u2.id, timestamp=dt7, type='following request')
    n2 = Notification(recipient_id=u1.id, sender_id=u2.id, timestamp=dt8, type='message')
    n3 = Notification(recipient_id=u1.id, sender_id=u3.id, timestamp=dt9, type='following request')
    n4 = Notification(recipient_id=u2.id, sender_id=u3.id, timestamp=dt10, type='following request')

    db.session.add_all([n1, n2, n3, n4])

    u1.set_password("123abc")
    u2.set_password("xyz")
    u3.set_password("qwerty")

    db.session.commit()

    return redirect(url_for('index'))
