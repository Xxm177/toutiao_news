import json
from datetime import datetime

from config.cache_conf import redis_client

# 缓存 key 约定
CATEGORIES_KEY = "cache:categories"
NEWS_LIST_PREFIX = "cache:news:list"
VIEW_PREFIX = "cache:news:views"
DIRTY_VIEWS_KEY = "cache:news:dirty_views"

CACHE_TTL = 5 * 60  # 新闻列表、分类缓存 5 分钟

# 序列化时保留的字段（跟数据库列名一致）
NEWS_FIELDS = ["id", "title", "description", "content", "image", "author",
               "category_id", "views", "publish_time", "created_at", "updated_at"]
CATEGORY_FIELDS = ["id", "name", "sort_order", "created_at", "updated_at"]


def to_dict(obj, fields: list[str]) -> dict:
    """把 ORM 对象转成普通字典，日期转成字符串，方便存进 Redis"""
    data = {}
    for f in fields:
        v = getattr(obj, f, None)
        if isinstance(v, datetime):
            v = v.isoformat()
        data[f] = v
    return data


# ---------- 分类缓存 ----------
async def get_categories_cache():
    val = await redis_client.get(CATEGORIES_KEY)
    return json.loads(val) if val else None


async def set_categories_cache(data: list[dict]) -> None:
    await redis_client.set(CATEGORIES_KEY, json.dumps(data, default=str), ex=CACHE_TTL)


# ---------- 新闻列表缓存 ----------
def _news_list_key(category_id: int, offset: int, limit: int) -> str:
    return f"{NEWS_LIST_PREFIX}:{category_id}:{offset}:{limit}"


async def get_news_list_cache(category_id: int, offset: int, limit: int):
    val = await redis_client.get(_news_list_key(category_id, offset, limit))
    return json.loads(val) if val else None


async def set_news_list_cache(category_id: int, offset: int, limit: int, data: list[dict]) -> None:
    await redis_client.set(_news_list_key(category_id, offset, limit),
                           json.dumps(data, default=str), ex=CACHE_TTL)


# ---------- 浏览量计数 ----------
async def incr_views(news_id: int) -> int:
    """浏览量 +1，返回该新闻自上次同步以来的累计增量"""
    return await redis_client.incr(f"{VIEW_PREFIX}:{news_id}")


async def get_views_increment(news_id: int) -> int:
    val = await redis_client.get(f"{VIEW_PREFIX}:{news_id}")
    return int(val) if val else 0


async def mark_dirty_view(news_id: int) -> None:
    """把新闻标记为‘有浏览量待写回数据库’"""
    await redis_client.sadd(DIRTY_VIEWS_KEY, news_id)


async def get_dirty_views() -> set[str]:
    return await redis_client.smembers(DIRTY_VIEWS_KEY)


async def clear_view(news_id: int) -> None:
    """写回数据库后，清掉该新闻的计数"""
    await redis_client.srem(DIRTY_VIEWS_KEY, news_id)
    await redis_client.delete(f"{VIEW_PREFIX}:{news_id}")
