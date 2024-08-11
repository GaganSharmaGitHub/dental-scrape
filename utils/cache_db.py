import redis
import config


class __RedisManager:
    def initialize(self):
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,
        )

    async def set_value(self, key: str, value: str):
        self.redis_client.set(key, value)

    async def get_value(self, key: str):
        return self.redis_client.get(key)

    async def delete_value(self, key: str):
        return self.redis_client.delete(key)

    def terminate(self):
        print("DB Connection terminated.")


cache_database = __RedisManager()
