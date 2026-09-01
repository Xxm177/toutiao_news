"""建表脚本：一条命令建好所有数据库表。

用法：python init_db.py
"""
import asyncio

from config.db_conf import async_engine
from models.users import Base as UserBase
from models.news import Base as NewsBase
from models.favorites import Base as FavoriteBase
from models.history import Base as HistoryBase


async def main():
    async with async_engine.begin() as conn:
        # 按依赖顺序建表：先 user、news，再 favorite、history（有外键）
        await conn.run_sync(UserBase.metadata.create_all)
        await conn.run_sync(NewsBase.metadata.create_all)
        await conn.run_sync(FavoriteBase.metadata.create_all)
        await conn.run_sync(HistoryBase.metadata.create_all)
    await async_engine.dispose()
    print("数据库表创建完成")


if __name__ == "__main__":
    asyncio.run(main())
