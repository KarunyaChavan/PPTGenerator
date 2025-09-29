from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = StringField('Department', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', 
                               validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ReviewForm(FlaskForm):
    feedback = TextAreaField('Feedback', validators=[DataRequired(), Length(min=1, max=500)])
    status = SelectField('Status', choices=[
        ('approved', 'Approve'),
        ('rejected', 'Reject')
    ], validators=[DataRequired()])
    submit = SubmitField('Submit Review')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class SlideContentForm(FlaskForm):
    title = StringField('Slide Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Slide Content', validators=[DataRequired()])

class PresentationForm(FlaskForm):
    title = StringField('Presentation Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    agenda = TextAreaField('Agenda (one item per line)', validators=[DataRequired()])
    
    # Dynamic slide content fields will be added via JavaScript
    slides_data = TextAreaField('Slides Data (JSON)', validators=[DataRequired()])
    
    submit = SubmitField('Generate Presentation')

class AdminReviewForm(FlaskForm):
    action = SelectField('Action', 
                        choices=[('approve', 'Approve'), ('reject', 'Reject')],
                        validators=[DataRequired()])
    notes = TextAreaField('Review Notes', validators=[Length(max=1000)])
    submit = SubmitField('Submit Review')