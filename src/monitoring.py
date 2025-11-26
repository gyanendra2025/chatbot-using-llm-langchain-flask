import os
import time
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps

# Production logging setup
handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.basicConfig(level=logging.INFO, handlers=[handler, logging.StreamHandler()])
logger = logging.getLogger(__name__)

if os.getenv("LANGCHAIN_TRACING") == "true":
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")

try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    if dsn := os.getenv("SENTRY_DSN"):
        sentry_sdk.init(dsn=dsn, integrations=[FlaskIntegration()], traces_sample_rate=0.1)
except ImportError: pass

def log_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            res = func(*args, **kwargs)
            logger.info(f"[SUCCESS] {func.__name__} in {time.time()-start:.2f}s")
            return res
        except Exception as e:
            logger.error(f"[ERROR] {func.__name__} failed: {e}")
            raise
    return wrapper

def log_metrics(endpoint, query, answer, latency):
    logger.info(f"[METRICS] {endpoint} | {latency:.2f}s")

def log_voice_metrics(endpoint, duration, trans, answer, latency):
    logger.info(f"[VOICE] {endpoint} | Aud:{duration:.1f}s | Lat:{latency:.2f}s")

def log_error(endpoint, msg, context=None):
    logger.error(f"[ERROR] {endpoint}: {msg} {f'| {context}' if context else ''}")
