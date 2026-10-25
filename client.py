import sys, re, math, time
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

class SemanticCacheQueryMatcherClient:
    """
    Sub-millisecond semantic query matcher and cache layer.
    Computes TF term frequency vectors and cosine similarity against indexed queries
    to return cached LLM responses without redundant inference costs.
    """
    def __init__(self, similarity_threshold=0.80, default_ttl_sec=3600.0):
        self.cache = {}
        self.similarity_threshold = similarity_threshold
        self.default_ttl = default_ttl_sec
        self.total_queries = 0
        self.hits = 0

    def _tokenize(self, text):
        return Counter(re.findall(r"\w+", text.lower()))

    def _cosine_similarity(self, c1, c2):
        intersection = set(c1.keys()) & set(c2.keys())
        numerator = sum(c1[x] * c2[x] for x in intersection)
        sum1 = sum(c1[x]**2 for x in c1.keys())
        sum2 = sum(c2[x]**2 for x in c2.keys())
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator: return 0.0
        return float(numerator) / denominator

    def set(self, query, response_payload, ttl_sec=None):
        ttl = ttl_sec or self.default_ttl
        self.cache[query] = {
            "tokens": self._tokenize(query),
            "response": response_payload,
            "hits": 0,
            "created_at": time.time(),
            "expires_at": time.time() + ttl
        }
        return {"status": "success", "cached_query": query, "ttl_sec": ttl}

    def get(self, query):
        self.total_queries += 1
        query_tokens = self._tokenize(query)
        now = time.time()

        best_match = None
        highest_sim = 0.0

        for key, entry in list(self.cache.items()):
            if now > entry["expires_at"]:
                del self.cache[key]
                continue
            sim = self._cosine_similarity(query_tokens, entry["tokens"])
            if sim > highest_sim:
                highest_sim = sim
                best_match = key

        if highest_sim >= self.similarity_threshold and best_match:
            self.hits += 1
            entry = self.cache[best_match]
            entry["hits"] += 1
            return {
                "status": "success",
                "cache_hit": True,
                "similarity_score": round(highest_sim, 4),
                "matched_query": best_match,
                "response": entry["response"],
                "cache_metrics": {
                    "total_queries": self.total_queries,
                    "hit_rate_pct": round(self.hits / self.total_queries * 100, 1)
                }
            }

        return {
            "status": "success",
            "cache_hit": False,
            "similarity_score": round(highest_sim, 4),
            "matched_query": best_match if highest_sim > 0 else None,
            "response": None,
            "cache_metrics": {
                "total_queries": self.total_queries,
                "hit_rate_pct": round(self.hits / self.total_queries * 100, 1)
            }
        }
