from client import SemanticCacheQueryMatcherClient
import sys, json
sys.stdout.reconfigure(encoding='utf-8')

def main():
    cache = SemanticCacheQueryMatcherClient(similarity_threshold=0.75)
    print("=== SEMANTIC CACHE QUERY MATCHER ===")

    # 1. Warm cache with canonical query
    q1 = "How do I calculate customer retention rate for SaaS?"
    ans1 = "Retention rate = ((E - N) / S) * 100 where E is ending users, N is new users, S is starting users."
    cache.set(q1, ans1)
    print()
    print(f"1. Indexed Query: '{q1}'")

    # 2. Query with semantic variation
    q2 = "Calculate SaaS customer retention rate formula"
    res2 = cache.get(q2)
    print()
    print(f"2. Varied Query: '{q2}'")
    print(f"   Result: Hit={res2['cache_hit']} | Similarity={res2['similarity_score']}")
    print(f"   Cached Response: {res2['response']}")

    # 3. Query with completely different topic
    q3 = "What is the capital of France?"
    res3 = cache.get(q3)
    print()
    print(f"3. Unrelated Query: '{q3}'")
    print(f"   Result: Hit={res3['cache_hit']} | Similarity={res3['similarity_score']}")
    print(f"   Overall Cache Hit Rate: {res3['cache_metrics']['hit_rate_pct']}%")

if __name__ == "__main__":
    main()
