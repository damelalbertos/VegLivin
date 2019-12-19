from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

from app import photos
from app.models import User


# def email_exists(form, field):
#     if User.select().where(User.email == field.data).exists():
#         raise ValidationError('User with that email already exists.')


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
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Sign up')


class EditProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    v_Status = TextAreaField('V Status', validators=[Length(min=0, max=14)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')


class PostForm(FlaskForm):
    content = TextAreaField("Post Here.", validators=[DataRequired(), Length(min=1, max=140)])
    # image = FileField("Image", validators=[FileAllowed(photos, 'Image Only!'), FileRequired('File was empty!')])
    submit = SubmitField('Submit')


class EventForm(FlaskForm):
    name = TextAreaField('Event Name', validators=[DataRequired()])
    date = DateTimeField('Event Date', format='%m/%d/%Y', validators=[DataRequired])
    # image
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    body = StringField("Post", validators=[DataRequired])
    submit = SubmitField("Submit")
