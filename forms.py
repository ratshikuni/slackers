from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')]
    )
    role = SelectField(
        'Role', choices=[('student', 'Student'), ('teacher', 'Teacher')], validators=[DataRequired()]
    )
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    
    submit = SubmitField('Login')

class TutorApplicationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    matric_certificate = FileField('Matric Certificate', validators=[DataRequired()])
    id_document = FileField('ID Document', validators=[DataRequired()])
    submit = SubmitField('Proceed')

class ManagementApplicationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    qualification_certificate = FileField('Qualification Certificate', validators=[DataRequired()])
    cv = FileField('Curriculum Vitae (CV)', validators=[DataRequired()])
    id_document = FileField('ID Document', validators=[DataRequired()])
    submit = SubmitField('Proceed')