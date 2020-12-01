echo "Implicit Grant"

cd ..
UUID=$(./manager.py --id=1 uuid)
cd -

curl -X POST  -c "./cookiefile" \
             -d '{"user":"demo", "password":"demo"}'  \
             -H "accept: application/json" \
             -H "Content-Type: application/json" \
             "http://127.0.0.1:5000/login"

# zapytanie curl zwraca href zamiast przekierowania

RET=$(curl -X GET -b "./cookiefile" \
            "http://127.0.0.1:5000/oauth/authorize?redirect_uri=http%3A%2F%2F127.0.0.1%3A3000&response_type=code&client_id=$UUID&state=state_test&response_mode=query" \
)


URL=$(python <(cat <<PYTHON
ret='''$RET'''
l=ret.rstrip()
x=l.find('href=')
if x>0:
  l=l[x+6:]
  x1=l.find('"')
  print(l[:x1])
PYTHON
))


if [[ -z "$URL" ]];then
  echo "nie ma przekierowania"
  echo $RET
else
  echo url=$URL
  echo "przekierowanie"
  curl -X GET $URL
fi
