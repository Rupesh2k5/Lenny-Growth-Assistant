import requests, json
BASE_URL = "http://localhost:8000"

print("1. Creating Session (Sending chat)...")
res = requests.post(f"{BASE_URL}/api/chat/stream", json={"session_id": "test-session-99", "message": "What is PMF according to Sean Ellis?", "provider": "mock"}, stream=True)
full_text = ""
for line in res.iter_lines():
    if line:
        data = line.decode("utf-8").replace("data: ", "")
        try:
            full_text += json.loads(data).get("token", "")
        except:
            pass
print("Chat Response length:", len(full_text))

print("\n2. Requesting Ship30 Essay...")
res = requests.post(f"{BASE_URL}/api/skills/ship30", json={"session_id": "test-session-99", "topic": "Finding PMF", "target_length": 1250, "provider": "mock"})
data = res.json()
print("Ship30 Response JSON keys:", data.keys())
art_id = data.get("artifact_id")
print("Ship30 Artifact ID:", art_id)

if art_id:
    print("\n3. Fetching Artifact...")
    res = requests.get(f"{BASE_URL}/api/artifacts/{art_id}")
    print("Artifact Title:", res.json().get("title"))

print("\n4. List Sources...")
res = requests.get(f"{BASE_URL}/api/sources")
print(f"Total Sources: {len(res.json())}")
