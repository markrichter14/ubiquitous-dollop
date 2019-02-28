from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

class MovieForm(FlaskForm):
    file_name = StringField('File Name', validators=[DataRequired()])
    path_name = StringField('Path Name', validators=[DataRequired()])
    dir_name = StringField('Folder Name', validators=[DataRequired()])
    submit = SubmitField('Move Movie')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')