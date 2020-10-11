__version__ = "0.0.1"

from flask import Flask
app=Flask(__name__, template_folder='templates')

from .config import init
init(False)

from .endpoints import define
define()

