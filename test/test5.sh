echo "OpenID - id_token"
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
            "http://127.0.0.1:5000/openid/authorize?response_type=id_token&state=stat1&client_id=$UUID&scope=openid&redirect_uri=http%3A%2F%2F127.0.0.1%3A3000&id=1&display=page&response_mode=query" 
