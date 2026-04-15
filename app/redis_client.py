import redis
import json

REDIS_HOST = "localhost"
REDIS_PORT = 6379
QUEUE_NAME = "log_queue"

client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def push_log(event: dict):
    client.lpush(QUEUE_NAME, json.dumps(event))


def pop_log():
    return client.brpop(QUEUE_NAME, timeout=0)

def get_queue_depth():
    return client.llen(QUEUE_NAME)