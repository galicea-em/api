# coding: utf-8

from flask import request, flash, redirect, render_template, url_for
from flask_login import current_user, logout_user, login_user, LoginManager

from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField
from wtforms import validators

from conf import app

from model import selected_dm
if selected_dm()=='sketch':

  def flask_login():
    return render_template("nologin.html")
else:
  from model.sql_model import User

  login_manager = LoginManager()
  login_manager.init_app(app)
  login_manager.login_view = "login"
  login_manager.login_message_category = "warning"
  from pprint import pprint
  pprint(current_user)

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

  @app.route("/login", methods=["GET", "POST"])
  def login():
    form = LoginForm()
    if form.validate_on_submit():
      res=User.query.filter_by(login=form.username.data)
      current_user = res.one() if res else None
      login_user(current_user)
      flash("Logged in successfully.", "success")
      return redirect(request.form.get('next') or url_for(".index"))
    else:
      redirectUri = request.args.get('redirect_uri')
      return render_template("login.html", form=form, next=redirectUri)


  @app.route("/logout")
  def logout():
      logout_user()
      flash("You have been logged out.", "success")
      return redirect(url_for(".login"))

  @app.route("/index")
  def index():
    return render_template("nologin.html")
