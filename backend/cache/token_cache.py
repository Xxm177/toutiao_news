from config.cache_conf import redis_client

TOKEN_PREFIX = "token:"
TOKEN_TTL = 7 * 24 * 60 * 60  # 登录凭证 7 天后自动失效


async def set_token(token: str, user_id: int) -> None:
    """登录成功后，把凭证写进 Redis，7 天后自动过期"""
    await redis_client.set(TOKEN_PREFIX + token, user_id, ex=TOKEN_TTL)


async def get_user_id_by_token(token: str) -> int | None:
    """根据凭证取出用户 id，凭证不存在或已过期返回 None"""
    val = await redis_client.get(TOKEN_PREFIX + token)
    return int(val) if val is not None else None


async def delete_token(token: str) -> None:
    """删除凭证（退出登录时用）"""
    await redis_client.delete(TOKEN_PREFIX + token)
