# coding: utf-8

from flask_login import current_user, LoginManager
from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField
from wtforms import validators
from conf import app

from model.sql_model import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
  return User.query.filter_by(id=user_id).one()

class LoginForm(Form):
  username = StringField(u'Identyfikator', validators=[validators.required()])
  password = PasswordField(u'Hasło', validators=[validators.optional()])

  def validate(self):
    check_validate = super(LoginForm, self).validate()
    # if our validators do not pass
    if not check_validate:
      return False
    user = User.query.filter_by(login=self.username.data).one()
    if not user:
      self.username.errors.append(u'Błędny identyfikator')
      return False

    # Do the passwords match
    if not user.check_password(self.password.data):
      self.username.errors.append(u'Błędny identyfikator lub hasło')
      return False
    return True

