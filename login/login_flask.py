# coding: utf-8

from flask import request, flash, redirect, render_template, url_for
from flask_login import current_user, logout_user
from rest import ses_login, put_session
from conf import app

from model import selected_dm
if selected_dm()=='sketch':

  def flask_login():
    return render_template("protected.html")
else:
  from .login_form import LoginForm
  from model.sql_model import User

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
        username=current_user.login
        print(username)
        if username=='admin':
          return redirect('/index')
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

  from .login_decorator import login_required

  @app.route("/index")
  @login_required('admin')
  def index():
    return render_template("protected.html")

