echo "Python Client Test"
curl -X POST  -c "./cookiefile" \
             -d '{"user":"demo", "password":"demo"}'  \
             -H "accept: application/json" \
             -H "Content-Type: application/json" \
             "http://127.0.0.1:5000/login"

URI="http%3A%2F%2F127.0.0.1%3A3000"
URL="http://127.0.0.1:5000/oauth/authorize?redirect_uri=$URI&response_type=code&client_id=1&state=state_test&response_mode=query"

echo $URL

RET=$( curl -X GET -b "./cookiefile" $URL )


URL=$(python <(cat <<PYTHON
ret='''$RET'''
l=ret.rstrip()
x=l.find('href=')
if x>0:
  l=l[x+6:]
  x1=l.find('"')
  url=l[:x1]
  print(url.replace('&amp;','&'))
PYTHON
))


if [[ -z "$URL" ]];then
  echo "nie ma przekierowania"
  echo $RET
else
  echo url=$URL
  echo '--------------------------'
  curl -X GET $URL
fi
