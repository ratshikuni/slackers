from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

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