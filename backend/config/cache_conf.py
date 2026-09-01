import redis.asyncio as redis

# Redis 连接配置：程序启动后，各处通过这个 redis_client 读写 Redis
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)
