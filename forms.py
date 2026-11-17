from datetime import date, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, BooleanField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp, ValidationError
from content import PHOTOS


class EnquiryForm(FlaskForm):
    parent_name = StringField('Parent / guardian name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email address', validators=[DataRequired(), Email(), Length(max=254)])
    phone = StringField('Phone number', validators=[DataRequired(), Length(min=7, max=32), Regexp(r'^[+\d\s()\-]+$', message='Enter a valid phone number.')])
    child_first_name = StringField('Child’s first name (optional)', validators=[Optional(), Length(max=80)])
    age_range = SelectField('Child’s age range', choices=[('', 'Select an age range'), ('Under 3', 'Under 3 years'), ('3–4', '3–4 years'), ('4–5', '4–5 years'), ('5+', '5 years and above'), ('Not specified', 'Prefer to discuss')], validators=[Optional()])
    programme = SelectField('Area of interest', choices=[('', 'Help me choose'), ('early-learners', 'Early learners'), ('growing-explorers', 'Growing explorers'), ('ready-for-school', 'Ready for school')], validators=[Optional()])
    preferred_date = DateField('Preferred visit date', validators=[Optional()])
    message = TextAreaField('How can we help?', validators=[Optional(), Length(max=2500)])
    consent = BooleanField('I agree to be contacted about this enquiry and have read the privacy information.', validators=[DataRequired(message='Please agree so the school can respond to your enquiry.')])
    website = StringField('Leave this field empty', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Send enquiry')

    def validate_preferred_date(self, field):
        if field.data and not date.today() <= field.data <= date.today() + timedelta(days=365):
            raise ValidationError('Choose a date within the next 12 months.')


class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(), Email(), Length(max=254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=256)])
    submit = SubmitField('Sign in securely')


class StatusForm(FlaskForm):
    status = SelectField('Enquiry status', choices=[('new', 'New'), ('contacted', 'Contacted'), ('closed', 'Closed')])
    notes = TextAreaField('Private staff notes', validators=[Optional(), Length(max=5000)])
    submit = SubmitField('Save changes')


class DeleteForm(FlaskForm):
    submit = SubmitField('Delete permanently')


class PostForm(FlaskForm):
    title = StringField('Article title', validators=[DataRequired(), Length(max=160)])
    slug = StringField('URL slug', validators=[DataRequired(), Length(max=160), Regexp(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')])
    category = StringField('Category', validators=[DataRequired(), Length(max=40)])
    excerpt = TextAreaField('Short introduction', validators=[DataRequired(), Length(max=300)])
    body = TextAreaField('Article content', validators=[DataRequired(), Length(max=20000)])
    image_key = SelectField('Featured image', choices=[(key, photo['label']) for key, photo in PHOTOS.items()])
    published = BooleanField('Publish on the website')
    submit = SubmitField('Save article')
