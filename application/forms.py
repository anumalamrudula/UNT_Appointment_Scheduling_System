from flask_wtf import FlaskForm
import wtforms
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, Regexp
from application.models import User, Universitymail


class LoginForm(FlaskForm):
    email   = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    email   = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Regexp(regex = '^(?=.*[A-Z])(?=.*[!@#$&*_])(?=.*[0-9])(?=.*[a-z]).{6,15}$', message = "Password must contain an uppercase letter, a lowercase letter, a digit, a special character, with length between 6 and 15.")])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired(),EqualTo('password')])
    first_name = StringField("First Name", validators=[DataRequired(),Length(min=2,max=55)])
    last_name = StringField("Last Name", validators=[DataRequired(),Length(min=2,max=55)])
    submit = SubmitField("Register Now")

    def validate_email(self,email):
        universityUser = Universitymail.objects(email=email.data).first()
        user = User.objects(email=email.data).first()
        if not(universityUser):
            raise ValidationError("You are not an authorized member of university")
        if user:
            raise ValidationError("You have already registered. Login to the application.")

class UpdateProfileForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[Optional(),Length(min=6,max=15)])
    new_password = PasswordField("New Password", validators=[Optional(), Regexp(regex = '^(?=.*[A-Z])(?=.*[!@#$&*_])(?=.*[0-9])(?=.*[a-z]).{6,15}$', message = "Password must contain an uppercase letter, a lowercase letter, a digit, a special character, with length between 6 and 15.")])
    password_confirm = PasswordField("Confirm Password", validators=[Optional(), EqualTo('new_password')])
    first_name = StringField("First Name", validators=[Length(min=2,max=55)])
    last_name = StringField("Last Name", validators=[Length(min=2,max=55)])
    submit = SubmitField("Save changes")

class SlotsForm(FlaskForm):
    slot = SelectField('slot', choices=[])

class AuthorizeMailForm(FlaskForm):
    email  = TextAreaField("Authorize Mail ID or IDs", validators=[DataRequired()])
    submit = SubmitField("Submit")

class ViewingListForm(FlaskForm):
    submit = SubmitField("Filter")

class ProfessorForm(FlaskForm):
    MailID   = StringField("Email", validators=[DataRequired(), Email()])
    Designation = StringField("Designation", validators=[DataRequired()])
    Name = StringField(" Full Name", validators=[DataRequired(),Length(min=2,max=55)])
    Dept = StringField("Department", validators=[DataRequired(),Length(min=2,max=10)])
    submit = SubmitField("Add Professor")

class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self,email):
        universityUser = Universitymail.objects(email=email.data).first()
        user = User.objects(email=email.data).first()
        if not(universityUser):
            raise ValidationError("You are not an authorized member of university")
        if not(user) and universityUser:
            raise ValidationError("Mail doesn't exist. Create an account.")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(), Regexp(regex = '^(?=.*[A-Z])(?=.*[!@#$&*_])(?=.*[0-9])(?=.*[a-z]).{6,15}$', message = "Password must contain an uppercase letter, a lowercase letter, a digit, a special character, with length between 6 and 15.")])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")

class GiantForm(FlaskForm):
    mailID_submit = wtforms.FormField(AuthorizeMailForm)
    Viewing_Details = wtforms.FormField(ViewingListForm)