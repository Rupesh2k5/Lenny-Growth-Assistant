import json
import requests

# -------------------------------------------------
# FastAPI base URL (keep the /api prefix!)
# -------------------------------------------------
BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/chat"

# -------------------------------------------------
# Request payload – no comments inside the dict!
# -------------------------------------------------
payload = {
    "session_id": "demo-session-1",
    "message": "Say hello"
    # `provider` and `stream` are optional; we rely on the .env defaults
}

# -------------------------------------------------
# Send the POST request and pretty‑print the JSON response
# -------------------------------------------------
response = requests.post(ENDPOINT, json=payload)
print(json.dumps(response.json(), indent=2))
