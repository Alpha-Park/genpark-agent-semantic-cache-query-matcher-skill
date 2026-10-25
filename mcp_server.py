import sys, json
from client import SemanticCacheQueryMatcherClient
sys.stdout.reconfigure(encoding='utf-8')

def handle_mcp():
    cache = SemanticCacheQueryMatcherClient()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps({"status": "ready", "skill": "genpark-agent-semantic-cache-query-matcher-skill"}))
        return
    req = json.loads(sys.stdin.read() or "{}")
    action = req.get("action", "get")
    q = req.get("query", "")
    if action == "set":
        ans = req.get("response", "")
        res = cache.set(q, ans)
    else:
        res = cache.get(q)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    handle_mcp()
