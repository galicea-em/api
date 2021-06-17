#!/usr/bin/env python3
# coding: utf-8
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020

from conf import app

debug=True
if __name__ == '__main__':
  app.run(debug=debug,
         host='0.0.0.0', 
         port=5000, 
         threaded=True)
