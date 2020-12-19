curl -X POST  -c "./cookiefile" \
             -d '{"user":"username", "password":"secret"}'  \
             -H "accept: application/json" \
             -H "Content-Type: application/json" \
             "http://127.0.0.1:5000/login/ldap"

