from functools import reduce
from typing import List

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import models
from search.models import Product


class SearchService:
    # total four weights are supported by postgres for relevancy
    # we can customize their values.
    # key: weight
    WEIGHTS = {
        "A": 0.8,
        "B": 0.6,
        "C": 0.4,
        "D": 0.2,
    }
    # set weights to tell how much relevancy we wants for each field
    # field_name: weight_key
    PRODUCT_SEARCH_FIELDS = {
        "name": "B",
        "description": "A",
    }

    async def get_weights(self) -> List[float]:
        weights = list(self.WEIGHTS.values())
        weights.sort()
        return weights

    async def sync_to_async(self, queryset: models.QuerySet[Product]) -> List[Product]:
        return [p async for p in queryset.values()]

    async def get_products(self) -> models.QuerySet[Product]:
        return Product.objects.all()

    async def normal_search(self, query: str) -> models.QuerySet[Product]:
        filters = models.Q()
        for field in self.PRODUCT_SEARCH_FIELDS.keys():
            filters |= models.Q(**{f"{field}__search": query})

        return Product.objects.filter(filters)

    async def anormal_search(self, query: str) -> List[Product]:
        return await self.sync_to_async(await self.normal_search(query))

    async def vector_search(self, query: str) -> models.QuerySet[Product]:
        return Product.objects.annotate(
            search=SearchVector(*list(self.PRODUCT_SEARCH_FIELDS.keys()))
        ).filter(search=query)

    async def avector_search(self, query: str) -> List[Product]:
        return await self.sync_to_async(await self.vector_search(query))

    async def ranking_search(
        self,
        query: str,
        min_rank: float = 0.01,
        search_type: str = "websearch",
        config: str = "english",
    ) -> models.QuerySet[Product]:
        vectors = [
            SearchVector(field, weight=weight)
            for field, weight in self.PRODUCT_SEARCH_FIELDS.items()
        ]
        query = SearchQuery(query, search_type=search_type, config=config)
        weights = await self.get_weights()

        return (
            Product.objects.annotate(
                rank=SearchRank(
                    reduce(lambda v1, v2: v1 + v2, vectors),
                    query,
                    weights=weights,
                ),
            )
            .filter(rank__gte=min_rank)
            .order_by("-rank")
        )

    async def aranking_search(self, query: str) -> List[Product]:
        return await self.sync_to_async(await self.ranking_search(query))
