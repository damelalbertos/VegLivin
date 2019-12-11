from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

from app import photos
from app.models import User


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


def validate_email(email):
    user = User.query.filter_by(email=email.data).first()
    if user is not None:
        raise ValidationError('Please use a different email address.')


def validate_username(username):
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
        raise ValidationError('Please use a different username.')


class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    dob = DateTimeField('DOB', format='%m/%d/%Y', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), email_exists])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Sign up')


class EditProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    v_Status = TextAreaField('V Status', validators=[Length(min=0, max=14)])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    content = TextAreaField("Post Here.")
    image = FileField("Image", validators=[FileAllowed(photos, 'Image Only!'), FileRequired('File was empty!')])
    submit = SubmitField('Submit')
