from upstash_redis.asyncio import Redis


def redis():
    return Redis.from_env()
