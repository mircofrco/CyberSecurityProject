# Register basic user
curl -X POST 'http://127.0.0.1:8000/auth/register' \
     -H 'Content-Type: application/json' \
     -d '{"email":"niklas@example.com","password":"S3cr3tP@ss"}'

# Register election admin user
curl -X POST 'http://127.0.0.1:8000/auth/register' \
     -H 'Content-Type: application/json' \
     -d '{"email":"admin@example.com","password":"AdminP@ss123"}'

# Register auditor user
curl -X POST 'http://127.0.0.1:8000/auth/register' \
     -H 'Content-Type: application/json' \
     -d '{"email":"auditor@example.com","password":"AuditorP@ss123"}'