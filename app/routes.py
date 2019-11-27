from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User, Event, UserToEvent , Post


@app.route('/')
@app.route('/index')
@login_required
def index():
    pass
    return render_template('index.html', title='Home', posts=posts)


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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/new_event', methods=['GET', 'POST'])
def new_event():
    pass
    return render_template('new_event.html', title='New event')


@app.route('/Home', methods=['GET', 'POST'])
def home():
    pass
    return render_template('Home.html', title='Home')


@app.route('/reset_db')
def reset_db():
    if current_user.is_authenticated:
        return redirect(url_for('reset_db'))
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()

    dt1 = datetime(2019, 10, 19)
    dt2 = datetime(2020, 10, 1)
    dt3 = datetime(2019, 4, 3)

    u1 = User(firstName='Amber', lastName='Elliott', DOB=10/5/00, v_Status='Vegan', email="Amber@gmail.com")
    u2 = User(firstName='Frank', lastName='Hood', DOB=6/14/87, v_Status='Flexitarian', email="Frank@gmail.com")
    u3 = User(firstName='Manon', lastName='Avery', DOB=12/5/19, v_Status='Vegetarian', email="Mano @gmail.com")

    e1 = Event(eventName='Vegan Pop-Up', location='Brooklyn, Ny', organizer='Louis Garner', dateTime=dt1)
    e2 = Event(eventName='Healthy Eating', location='Bronx, Ny', organizer='Tomas Jennings', dateTime=dt2)
    e3 = Event(eventName='Plant-Based Plantluck', location='Ithaca, Ny', organizer='Tobey Winter', dateTime=dt3)

    p1 = Post(post_details="I am looking for a vegan event for a kid", likes=5, comments=6, favorites=7, User=u1)
    p2 = Post(likes=20, comments=0, favorites=1, User=u2)
    p3 = Post(likes=100, comments=30, favorites=20, User=u3)

    u2e1 = UserToEvent(user=u1, event=e1)
    u2e2 = UserToEvent(user=u1, event=e2)
    u2e3 = UserToEvent(user=u2, event=e1)
    u2e4 = UserToEvent(user=u3, event=e3)

    db.session.add_all([u1, u2, u3, e1, e2, e3, p1, p2, p3, u2e1, u2e2, u2e3, u2e4])
    db.session.commit()

    return redirect(url_for('index'))
