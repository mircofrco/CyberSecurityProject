# Create DB tables
cd app/scripts || exit
python seed_roles.py

# Start FastAPIServer
cd ../.. || exit
uvicorn app.api.main:app --reload &

# Capture server PID (optional)
SERVER_PID=$!
echo "✅ Server started in background with PID $SERVER_PID"

# Wait until the server is responsive
echo "⏳ Waiting for FastAPI server to become responsive..."

MAX_RETRIES=30
RETRY_INTERVAL=1
COUNTER=0
until curl -s http://127.0.0.1:8000/docs > /dev/null; do
  sleep $RETRY_INTERVAL
  COUNTER=$((COUNTER + 1))
  if [ "$COUNTER" -ge "$MAX_RETRIES" ]; then
    echo "❌ Server did not respond in time. Exiting."
    exit 1
  fi
done
echo "✅ Server is responsive. Continuing with the script..."

echo "🆕 Trying to register a new users, admins and auditors..."
cd app/tests/bash || exit
chmod +x register.sh
./register.sh
# Output should be something like:
# {"id":"1a3757e1-fd4f-4aa7-8e42-00c40049a38f","email":"alice@example.com","is_active":true,"is_superuser":false,"is_verified":false,"mfa_enabled":false}%
echo "✅ Users registered successfully"

sleep 2

# Login and extract token
echo "🔐 Trying to log in..."
chmod +x login.sh
LOGIN_RESPONSE=$(./login.sh)
echo "🔓 Login response: $LOGIN_RESPONSE"

# Extract token using jq
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Failed to extract access token."
  exit 1
fi

export TOKEN
echo "✅ Extracted token: $TOKEN"

# Use token to call protected endpoint
echo "🔍 Calling protected endpoint /auth/users/me..."
curl -s -X GET "http://127.0.0.1:8000/auth/users/me" \
     -H "Authorization: Bearer $TOKEN"

echo
echo "✅ Protected endpoint call complete."

# Kill the FastAPI server
echo
if ps -p $SERVER_PID > /dev/null; then
  echo "🛑 Killing FastAPI server (PID $SERVER_PID)..."
  kill $SERVER_PID
  echo "✅ Server process stopped."
else
  echo "⚠️ Server process not found. Maybe it already exited."
fi
