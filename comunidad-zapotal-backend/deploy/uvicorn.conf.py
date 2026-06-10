import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logs
accesslog = "./logs/uvicorn_access.log"
errorlog = "./logs/uvicorn_error.log"
loglevel = "info"
