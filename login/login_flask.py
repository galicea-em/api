# coding: utf-8

from flask import request, flash, redirect, render_template, url_for
from flask_login import current_user, logout_user, login_user, LoginManager

from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField
from wtforms import validators

from rest import ses_login, get_session_auth_time, get_session_uid, get_user_id, put_session
from rest import time_to_now, LOGIN_TIMEOUT

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
      if current_user:
        user_id = current_user.id
#        login_user(current_user)
        sid = ses_login(user_id)
        put_session(sid, user_id)
        flash("Logged in successfully.", "success")
#        return redirect(request.form.get('redirect_uri') or url_for(".index"))
        scope = request.form.get('scope')
        state = request.form.get('state')
        clientID = request.form.get('client_id')
        redirectUri = request.form.get('redirect_uri')
        response_mode = request.form.get('response_mode')
        if not response_mode: response_mode = 'query'
        if scope:
          return render_template("consent.html", form=form,
                           action="/oauth/authorize",
                           redirect_uri=redirectUri,
                           scope=scope,
                           state=state,
                           response_mode=response_mode,
                           client_id=clientID
                           )
        else:
          return redirect(url_for("oauth_authorize_class",
                                  response_type='token',
                                  response_mode=response_mode,
                                  redirect_uri=redirectUri,
                                  scope=scope,
                                  state=state,
                                  client_id=clientID
                                  ))
    scope = request.args.get('scope')
    state = request.args.get('state')
    clientID = request.args.get('client_id')
    redirectUri = request.args.get('redirect_uri')
    response_mode = request.args.get('response_mode')
    if not response_mode: response_mode = 'query'
    if not state: state = ''
    if not scope: scope = ''
    if not clientID: clientID = ''
    if not redirectUri: redirectUri = ''
    return render_template("login.html", form=form,
                           redirect_uri=redirectUri,
                           scope=scope,
                           state=state,
                           response_mode=response_mode,
                           client_id=clientID
                           )


  @app.route("/logout")
  def logout():
      logout_user()
      flash("You have been logged out.", "success")
      return redirect(url_for(".login"))

  @app.route("/index")
  def index():
    return render_template("nologin.html")
