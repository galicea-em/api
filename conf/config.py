from . import app
import logging
import configparser

config = configparser.ConfigParser()

def init(log):
  config.read("conf/api.ini")
  secret_csrf=config['app']['secret_csrf']

  if not 'db_path' in config['db']:
    db_password=config['db']['password']
    db_user=config['db']['user']
    db_host=config['db']['host']
    db_name=config['db']['name']
    config['db']['db_path'] = 'mysql://%s:%s@%s/%s' % (db_user, db_password, db_host, db_name)

  app.config['SECRET_KEY'] = config['app']['secret_csrf']
  app.config['SQLALCHEMY_DATABASE_URI'] = config['db']['db_path']
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
  app.config['RESTX_MASK_HEADER']=False
  app.config['RESTX_MASK_SWAGGER']=False
  app.config.setdefault('RESTX_MASK_SWAGGER', True)
  app.secret_key = config['app']['secret']
  if log:
    logfile = '../log/' + config['app']['logfilename']
    logging.basicConfig(filename=logfile, level=logging.DEBUG)

