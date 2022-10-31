from typing import List

from django.contrib.postgres.search import SearchVector
from django.db import models

from .models import Product


def prep_product_search_vector_index(
    products: models.QuerySet[Product] | List[Product],
    save: bool = True,
):
    for product in products:
        product.search_vector = SearchVector(*Product.SEARCH_VECTOR_FIELDS)
        product.search_index_dirty = False

    if save:
        Product.objects.bulk_update(products, ["search_vector", "search_index_dirty"])

    return products
