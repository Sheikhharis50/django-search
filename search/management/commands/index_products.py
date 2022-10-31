import asyncio

from django.core.management.base import BaseCommand

from search.services import SearchService
from search.utils import prep_product_search_vector_index


class Command(BaseCommand):
    help = "Index Products"

    def handle(self, *args, **options):
        service = SearchService()
        products = asyncio.run(service.get_products())

        prep_product_search_vector_index(products)

        self.stdout.write(f"{products.count()} Products are indexed.")
