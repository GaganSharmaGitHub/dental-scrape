from typing import Optional
from pydantic import BaseModel, Field


class ProductDetails(BaseModel):
    product_title: str
    product_price: int
    path_to_image: str
