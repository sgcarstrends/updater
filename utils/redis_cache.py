from config.redis import redis


async def cache_checksum(file_name: str, checksum: str):
    try:
        return await redis().set(f"checksum:{file_name}", checksum)
    except Exception as e:
        print(f"Error caching checksum: {e}")
        return None


async def get_cached_checksum(file_name: str):
    try:
        return await redis().get(f"checksum:{file_name}")
    except Exception as e:
        print(f"Error retriving cached checksum: {e}")
        return None
