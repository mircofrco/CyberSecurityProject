curl -X POST 'http://127.0.0.1:8000/auth/register' \
     -H 'Content-Type: application/json' \
     -d '{"email":"alice@example.com","password":"S3cr3tP@ss"}'