echo "Authorization code grant"

URI="http%3A%2F%2F127.0.0.1%3A3000"

curl -X POST  -c "./cookiefile" \
             -d '{"user":"demo", "password":"demo"}'  \
             -H "accept: application/json" \
             -H "Content-Type: application/json" \
             "http://127.0.0.1:5000/login"


AUTH_CODE=$(curl -X GET -b "./cookiefile" \
            -H "accept: application/json" \
            "http://127.0.0.1:5000/oauth/authorize?redirect_uri=$URI&response_type=code&client_id=1" \
|  python <(cat <<PYTHON
import sys
for line in sys.stdin:
  l=line.rstrip()
  x=l.find('code')
  if x>0:
    l=l[x+5:]
    x1=l.find('"')
    x2=l.find('>')
    x3=x1 if x1<x2 else x2
    print(l[:x3])
PYTHON
))


echo "code=$AUTH_CODE"
echo "---------------"
echo 'zapytanie o kod dostepu:'

curl -X POST -H "accept: application/json" \
             -H "Content-Type: application/x-www-form-urlencoded" \
             --data "client_id=1&scope=&code=$AUTH_CODE&redirect_uri=$URI&grant_type=authorization_code&client_secret=secret" \
             http://127.0.0.1:5000/oauth/token
