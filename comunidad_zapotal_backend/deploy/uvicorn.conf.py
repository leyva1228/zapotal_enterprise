import multiprocessing
import os

bind = "127.0.0.1:8000"
workers = int(os.getenv("UVICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logs
accesslog = "./logs/uvicorn_access.log"
errorlog = "./logs/uvicorn_error.log"
loglevel = os.getenv("UVICORN_LOG_LEVEL", "info")
