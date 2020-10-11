#coding: utf-8
# authors: Jerzy Wawro
# (C) Galicea 2020


import os
import sys

PROJECT_ROOT = os.path.abspath(os.curdir)
sys.path.insert(0, PROJECT_ROOT)

activate_this = os.path.abspath(os.path.join(PROJECT_ROOT,'..'))+'/venv/bin/activate_this.py'

# Python 2.7: execfile(activate_this, dict(__file__=activate_this))
with open(activate_this) as infile:
    exec(infile.read(), dict(__file__=activate_this))

from conf import app as application
#application.run(debug=True)


