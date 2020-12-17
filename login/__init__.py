__version__ = "0.0.1"

def init_login(sel):
  if sel=='flask':
    from  . import login_flask
  elif sel=='simple':
    from  . import login_simple
  from  . import login_json

