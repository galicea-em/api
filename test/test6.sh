echo "OpenID - acces token"

#cd ../..
#source venv/bin/activate > /dev/null
#cd -  > /dev/null

cd ..
UUID=$(./manager.py --id=1 uuid)
cd -


curl -X POST  -c "./cookiefile" \
             -d '{"user":"demo", "password":"demo"}'  \
             -H "accept: application/json" \
             -H "Content-Type: application/json" \
             "http://127.0.0.1:5000/login"

curl -X GET -b "./cookiefile" \
            -H "accept: application/json" \
            "http://127.0.0.1:5000/openid/authorize?response_type=token&state=stat1&client_id=$UUID&scope=openid&redirect_uri=http%3A%2F%2F127.0.0.1%3A3000&id=1&display=page&response_mode=query" 

TOKEN=$(curl -X GET -b "./cookiefile" \
            -H "accept: application/json" \
            "http://127.0.0.1:5000/openid/authorize?response_type=token&state=stat1&client_id=$UUID&scope=openid&redirect_uri=http%3A%2F%2F127.0.0.1%3A3000&response_mode=query" \
|  python <(cat <<PYTHON
import sys
for line in sys.stdin:
  l=line.rstrip()
  x=l.find('access_token')
  if x>0:
    l=l[x+13:]
    x1=l.find('&')
    x2=l.find('>')
    x3=x1 if x1<x2 else x2
    print(l[:x3])
PYTHON
))


echo "token=$TOKEN"


curl -X GET "http://127.0.0.1:5000/openid/userinfo" -H "accept: application/json" \
             -H "Authorization: Bearer $TOKEN" 


