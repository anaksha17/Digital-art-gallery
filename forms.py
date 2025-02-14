from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FloatField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from datetime import datetime
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Log in')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    user_type = SelectField('I am a',
        choices=[('customer', 'Customer'), ('artist', 'Artist'), ('admin', 'Admin'), ('curator', 'Curator')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Sign up')


class AuctionForm(FlaskForm):
    starting_price = FloatField('Starting Price', validators=[DataRequired()])
    start_date = DateTimeField('Start Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    end_date = DateTimeField('End Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])

    def validate_start_date(self, field):
        if field.data <= datetime.now():
            raise ValidationError('Start date must be in the future.')

    def validate_end_date(self, field):
        if field.data <= self.start_date.data:
            raise ValidationError('End date must be after start date.')

from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError

class AuctionScheduleForm(FlaskForm):
    auction_id = SelectField(
        'Select Auction',
        validators=[DataRequired(message='Please select an auction')],
        choices=[],  # Will be populated with auction choices
        coerce=int
    )
    
    artwork_ids = SelectMultipleField(
        'Select Artworks',
        validators=[DataRequired(message='Please select at least one artwork')],
        choices=[],  # Will be populated with artwork choices
        coerce=int
    )

    def validate_artwork_ids(self, field):
        selected = field.data
        if not selected:
            raise ValidationError('Please select at least one artwork.')
        if len(selected) > 3:
            raise ValidationError('An auction can have a maximum of 3 artworks.')