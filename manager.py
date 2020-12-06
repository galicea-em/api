#!/usr/bin/env python3
# coding: utf-8
# authors: Jerzy Wawro
# (C) Galicea 2020

from model import set_context, selected_dm

DB_PATH='sqlite:///api.db'

def create():
  set_context(True, creating=True)
  selected_dm(DB_PATH)
  from model import dm
  dm.create_db()

def demo():
  set_context(True, creating=False)
  selected_dm(DB_PATH)
  from model import dm
  a=dm.add_address(country='Poland')
  dm.add_user('demo', 'demo', name='John Down', email='jd@example.com', address_id=a)
  dm.add_client('demoapp', 'secret', 1, 'http://127.0.0.1:3000')

def uuid(id):
  set_context(True, creating=False)
  selected_dm(DB_PATH)
  from model import dm
  cl=dm.get_client(id)
  if cl:
    return cl.uuid
  else:
    return ''


def test():
  set_context(True, creating=False)
  selected_dm(DB_PATH)
  from model import dm
  print(dm.get_user(1))
  print(dm.get_user_id('demo','demo'))
  print(dm.get_client(1))


def user(ident, secret, email):
  set_context(True, creating=False)
  selected_dm(DB_PATH)
  from model import dm
  dm.add_user(ident, secret, email=email)

def client(ident, secret, uri, user_id=1):
  set_context(True, creating=False)
  selected_dm(DB_PATH)
  from model import dm
  dm.add_client(ident, secret, user_id, uri)

import argparse
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(description='API Manager.', formatter_class=RawTextHelpFormatter)
parser.add_argument('operation', help='''Operation:
   create - create daatabase schema
   demo - insert demo data to database
   test - select demo data
   user - register user
   client - register client
   uuid - client_id to uuid
''')
parser.add_argument('--ident', help='login/identifier for new object')
parser.add_argument('--secret', help='Secret/Password for new object')
parser.add_argument('--uri', help='Redirect URI')
parser.add_argument('--email', help='Option: user email', default='')
parser.add_argument('--id', help='Option: id (client\'s)', default='1')
parser.add_argument('--db', help='Database Path eg: sqlite:///demo.db')


if __name__ == '__main__':
  args = parser.parse_args()
  if not 'operation' in args:
    parser.print_help()
  else:
    if args.db:
      DB_PATH=args.db
    if args.operation == 'create':
      create()
    elif args.operation == 'demo':
      demo()
    elif args.operation == 'uuid':
      uu=uuid(args.id)
      print(uu if uu else 'Not found')
    elif args.operation == 'test':
      test()
    elif (args.operation == 'user') or (args.operation == 'client') :
      if (not args.ident) or (not args.secret):
        print('Mandatory parameters: ident, secret')
      else:
        if (args.operation == 'user'):
          user(args.ident,args.secret,args.email if args.email else '')
        else:
          if (not args.uri):
            print('Mandatory parameter: uri')
          else:
            client(args.ident,args.secret,args.uri)
    else:
      parser.print_help()

