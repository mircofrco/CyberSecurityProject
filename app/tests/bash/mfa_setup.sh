TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiOWZlNWIyNC1lNjUzLTQ1NjUtYjk2Ni1jNjUzZDc3ZmJkNTciLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc0OTI5NDU0NH0.MP9C6cL-pCqHKNVSt5uVWUQKKwpy_VmzA2yfSMDF6mU        # copy access_token from previous step
curl -X POST 'http://127.0.0.1:8000/mfa/setup' \
     -H "Authorization: Bearer $TOKEN"
