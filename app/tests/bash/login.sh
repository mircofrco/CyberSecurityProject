curl -X POST 'http://127.0.0.1:8000/auth/jwt/login' \
     -d 'username=alice@example.com&password=S3cr3tP@ss' \
     -H 'Content-Type: application/x-www-form-urlencoded'
