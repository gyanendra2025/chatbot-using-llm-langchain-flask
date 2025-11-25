import hashlib
import json
import os
from typing import Optional

redis_client = None
CACHE_BACKEND = "disabled"

def _init_client():
    url, token = os.getenv("UPSTASH_REDIS_REST_URL"), os.getenv("UPSTASH_REDIS_REST_TOKEN")
    if url and token:
        try:
            from upstash_redis import Redis
            return Redis(url=url, token=token), "upstash"
        except ImportError: pass
    
    try:
        import redis
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        client.ping()
        return client, "local"
    except Exception: return None, "disabled"

redis_client, CACHE_BACKEND = _init_client()

def get_cached_answer(query):
    if not redis_client: return None
    try:
        cached = redis_client.get(f"rag:{hashlib.md5(query.encode()).hexdigest()}")
        return json.loads(cached) if cached else None
    except Exception: return None

def cache_answer(query, answer, ttl=3600):
    if not redis_client: return False
    try:
        key = f"rag:{hashlib.md5(query.encode()).hexdigest()}"
        redis_client.set(key, json.dumps(answer))
        try: redis_client.expire(key, ttl)
        except Exception: redis_client.setex(key, ttl, json.dumps(answer))
        return True
    except Exception: return False

def get_cache_stats():
    if not redis_client: return {"status": "disabled"}
    if CACHE_BACKEND == "upstash": return {"status": "active", "backend": "upstash"}
    try:
        info = redis_client.info('stats')
        return {
            "status": "active",
            "backend": "local",
            "hits": info.get('keyspace_hits', 0),
            "misses": info.get('keyspace_misses', 0)
        }
    except Exception: return {"status": "error"}
