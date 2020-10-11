COMMANDLINE=False
CREATING=False
DB_PATH='sketch'
dm = None


def set_context(commandline, creating=False, db_path=None):
  global DB_PATH
  global COMMANDLINE
  global CREATING
  COMMANDLINE=commandline
  CREATING=creating
  if db_path:
    DB_PATH=db_path


def selected_dm(db_path=None):
  global DB_PATH
  global dm
  if db_path:
    DB_PATH=db_path
  if DB_PATH != 'sketch':
    from . import sql_model
    dm=sql_model.create_dm(DB_PATH)
  return DB_PATH

