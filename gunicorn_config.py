import multiprocessing
import os

# Configuração para Render
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
workers = int(os.getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = "gevent"
worker_connections = 1000
max_requests = 2000
max_requests_jitter = 200
timeout = 120
keepalive = 5
preload_app = True

# Logging
loglevel = os.getenv('LOG_LEVEL', 'info')
accesslog = '-'
errorlog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

def on_starting(server):
    server.log.info("🚀 Iniciando servidor Gunicorn na Render...")

def worker_int(worker):
    worker.log.info(f"💀 Worker {worker.pid} interrompido")

def on_exit(server):
    server.log.info("👋 Servidor Gunicorn finalizado")
