from pydantic import BaseModel


class FavoriteAdd(BaseModel):
    newsId: int
