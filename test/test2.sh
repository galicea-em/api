echo "Authorization code grant - to redirection"
curl -X POST  -c "./cookiefile" \
             -d '{"user":"demo", "password":"demo"}'  \
             -H "accept: application/json" \
             -H "Content-Type: application/json" \
             "http://127.0.0.1:5000/login"

curl -X GET -b "./cookiefile" \
            -H "accept: application/json" \
            "http://127.0.0.1:5000/oauth/authorize?redirect_uri=http%3A%2F%2F127.0.0.1%3A3000&response_type=code&client_id=1&scope=&state=" 
