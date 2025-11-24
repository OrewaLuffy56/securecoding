"""Redis RQ Worker for background job processing"""
import os
import redis
from rq import Worker, Queue, Connection

# Redis connection
redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
redis_conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(['default'], connection=redis_conn)
        print("🚀 RQ Worker started. Listening for jobs...")
        worker.work()
