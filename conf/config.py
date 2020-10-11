from . import app
import logging

secret = '-044344yrds++33'
dbname = 'api.db'
db_path='sqlite:///'+dbname
logname = "api.log"
secret_csrf='secret_csrf' # zabezpieczenie przed csrf

def init(log):
  app.config['SECRET_KEY'] = secret_csrf
  app.config['SQLALCHEMY_DATABASE_URI'] = db_path
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
  app.config['RESTX_MASK_HEADER']=False
  app.config['RESTX_MASK_SWAGGER']=False
  app.config.setdefault('RESTX_MASK_SWAGGER', True)
  app.secret_key = secret
  if log:
    logfile = '../log/' + logname
    logging.basicConfig(filename=logfile, level=logging.DEBUG)

