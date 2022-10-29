from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.utils.text import slugify


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(default="")
    description = models.TextField(default="", max_length=1000)
    price = models.FloatField(default=1.0)
    search_document = models.TextField(blank=True, default="")
    search_vector = SearchVectorField(blank=True, null=True)
    search_index_dirty = models.BooleanField(default=False)

    SEARCH_VECTOR_FIELDS = ["name", "description"]

    def __str__(self) -> str:
        return f"{self.name} {self.price}$"

    def save(self, *args, **kwargs) -> None:
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("-id",)
        # Generalized Inverted Indexes (GIN) are useful when an index
        # must map many values to one row, whereas B-Tree indexes are
        # optimized for when a row has a single key value.
        # https://www.postgresql.org/docs/current/gin-intro.html
        # https://devcenter.heroku.com/articles/postgresql-indexes#index-types
        indexes = [
            GinIndex(
                name="search_document_idx",
                fields=["search_document"],
                opclasses=[
                    "gin_trgm_ops"
                ],  # https://www.postgresql.org/docs/current/pgtrgm.html
            ),
            GinIndex(
                name="search_vector_idx",
                fields=["search_vector"],
            ),
        ]
