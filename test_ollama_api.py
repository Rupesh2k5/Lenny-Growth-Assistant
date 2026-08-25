import urllib.request, json

req = urllib.request.Request("http://localhost:11434/api/tags")
try:
    with urllib.request.urlopen(req) as res:
        print("Tags:", res.read().decode())
except Exception as e:
    print("Tags Error:", e)

req2 = urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps({"model": "llama3.1:8b", "messages": [{"role": "user", "content": "hello"}], "stream": False}).encode(), headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req2) as res:
        print("Chat:", res.read().decode())
except Exception as e:
    print("Chat Error:", e)
