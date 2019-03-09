from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField, BooleanField,
                    IntegerField, TextAreaField)
from wtforms.validators import (DataRequired, Length, Email, EqualTo, Regexp, 
                                Optional, ValidationError)

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

class ShowForm(FlaskForm):
    show_name = StringField('Show Name', validators=[DataRequired()])
    show_dir = StringField('Directory Name', validators=[DataRequired()])
    watching = BooleanField('Watching', default="checked")
    theTVDB_id = IntegerField('theTVDB ID', validators=[DataRequired()])
    theTVDB_name = StringField('theTVDB Name', validators=[DataRequired()])
    theTVDB_slug = StringField('theTVDB Slug')
    theTVDB_status = StringField('theTVDB Status')
    new_show_id = IntegerField('new_show_id')
    submit = SubmitField('Add Show')

class NewShowsForm(FlaskForm):
    new_show_names = TextAreaField('New Show Names', validators=[])
    text_file = FileField('Text File', validators=[FileAllowed(['txt', 'text'], 'Text files only!')])
    submit = SubmitField('Submit')

    def validate_new_show_names(self, new_show_names):
        print('Call validate_new_show_names')
        if not new_show_names.data and not self.text_file.data:
            raise ValidationError('Atleast one field must be filled')

    def validate_text_file(self, text_file):
        print('Call validate_text_file')
        if not self.new_show_names.data and not text_file.data:
            raise ValidationError('Atleast one field must be filled')

 


