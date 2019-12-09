from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User, Event, UserToEvent , Post , Friends, Notification


@app.route('/')
@app.route('/index')
@login_required
def index():
    pass
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
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
        person = User(first_name=form.firstname.data, last_name=form.lastname.data, dob=form.dob.data, email=form.email.data)
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


@app.route('/user/<email>')
@login_required
def user(email):
    user = User.query.filter_by(email=email).first_or_404()
    friends = Friends.query.filter_by(user_id=user.id).all()
    posts = user.posts
    return render_template('user.html', user=user, posts=posts, friends=friends)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.user_details = form.v_Status.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', email=current_user.email))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.v_Status.data = current_user.user_details
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



    e1 = Event(title='Vegan Pop-Up', location='Brooklyn, Ny', organizer='Louis Garner', start_time_date=dt4)
    e2 = Event(title='Healthy Eating', location='Bronx, Ny', organizer='Tomas Jennings', start_time_date=dt5)
    e3 = Event(title='Plant-Based Plantluck', location='Ithaca, Ny', organizer='Tobey Winter', start_time_date=dt6)

    p1 = Post(post_details="I am looking for a vegan event for a kid", likes=5, comments=6, favorites=7)
    p2 = Post(post_details="I hosting this event about healthy eating, please check it out", likes=20, comments=0, favorites=1)
    p3 = Post(post_details="Hey I am new to the site and looking for friends", likes=100, comments=30, favorites=20)

    u1 = User(first_name='Amber', last_name='Elliott', email="Amber@gmail.com", dob=dt1, user_details='Vegan', posts=[p1])
    u2 = User(first_name='Frank', last_name='Hood', email="Frank@gmail.com", dob=dt2, user_details='Flexitarian', posts=[p2])
    u3 = User(first_name='Manon', last_name='Avery', email="Manon@gmail.com", dob=dt3, user_details='Vegetarian', posts=[p3])

    u2e1 = UserToEvent(user=u1, event=e1)
    u2e2 = UserToEvent(user=u1, event=e2)
    u2e3 = UserToEvent(user=u2, event=e1)
    u2e4 = UserToEvent(user=u3, event=e3)

    db.session.add_all([u1, u2, u3, e1, e2, e3, p1, p2, p3, u2e1, u2e2, u2e3, u2e4])
    db.session.commit()

    f1 = Friends(user_id=u1.id, friend_id=u2.id)
    f2 = Friends(user_id=u1.id, friend_id=u3.id)
    f3 = Friends(user_id=u2.id, friend_id=u3.id)

    n1 = Notification(recipient_id=u1.id, sender_id=u2.id, timestamp=dt7, type='friend request')
    n2 = Notification(recipient_id=u1.id, sender_id=u2.id, timestamp=dt8, type='message')
    n3 = Notification(recipient_id=u1.id, sender_id=u3.id, timestamp=dt9, type='friend request')
    n4 = Notification(recipient_id=u2.id, sender_id=u3.id, timestamp=dt10, type='friend request')

    db.session.add_all([f1, f2, f3, n1, n2, n3, n4])

    u1.set_password("123abc")
    u2.set_password("xyz")
    u3.set_password("qwerty")

    db.session.commit()

    return redirect(url_for('index'))
