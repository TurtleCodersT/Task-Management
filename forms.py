from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, URL, Email, EqualTo
from flask_ckeditor import CKEditorField

class RegisterForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    name = StringField(label="Name/Username", validators=[DataRequired()])
    submit = SubmitField("Sign me up!")

class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Log me In!")

class NewTask(FlaskForm):
    task_name = StringField(label='What is the name of the task you want to create?: ', validators=[DataRequired()])
    description = StringField(label='Provide a more detailed description of what you task is: ', validators=[DataRequired()])
    speed = SelectField(label='Choose which of the following best describe how fast you need you task to be finished by: ', choices=['ASAP', "Within a few days", "I have at least a week or two", "One whole month to complete this", "Extremely long time 2 months or more"], validators=[DataRequired()])
    deadline = DateField(label='Enter the date you need to finish before: ', format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField(label='Enter the time you need to finish by: ', format='%H:%M')
    submit = SubmitField(label='Add task')

class ChangePriority(FlaskForm):
    new_priority = SelectField(label='Choose which of the following best describe how fast you need you task to be finished by: ', choices=['ASAP', "Within a few days", "I have at least a week or two", "One whole month to complete this", "Extremely long time 2 months or more"], validators=[DataRequired()])
    submit = SubmitField(label='Save changes')