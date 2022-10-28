import os
from functools import reduce
from typing import Dict, List, Tuple

from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.management.base import BaseCommand
from django.db import models

from search.models import Product


class Command(BaseCommand):
    help = "Search Products"

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

    def add_arguments(self, parser) -> None:
        return super().add_arguments(parser)

    def get_weights(self) -> List[float]:
        weights = list(self.WEIGHTS.values())
        weights.sort()
        return weights

    def print_products(self, products: models.QuerySet[Product]):
        for i, p in enumerate(products):
            print(f"Product # {i+1}")
            print("-" * 10)
            print(f"NAME = {p.name}")
            print(f"DESCRIPTION = {p.description}")
            print(f"PRICE = {p.price}")
            if hasattr(p, "rank"):
                print(f"RANK = {p.rank}")
            print("-" * 10, "\n")

    def print_interrupt_message(self, *args, **kwargs):
        print(*args, **kwargs)
        input("\nPress any key to continue.")

    def print_result(self, search_name: str, products: models.QuerySet[Product]):
        print("\nResults ", "+" * 26, "\n")
        print(search_name)
        print("+" * 20, "\n")
        self.print_products(products)
        print("\nEND ", "+" * 28)

    def print_result_to_file(
        self, products: models.QuerySet[Product], colums: List[str], sep: str = "\t"
    ):
        with open(os.path.join(settings.OUTPUT_DIR, "results.csv"), "w") as f:
            for i, c in enumerate(colums):
                if i != 0:
                    f.write(sep)
                f.write(c)
            for p in products:
                f.write("\n")
                for i, c in enumerate(colums):
                    if i != 0:
                        f.write(sep)
                    f.write(str(getattr(p, c, "")))

    def menu(self) -> Tuple[int, Dict[int, str]]:
        choices: Dict[int, str] = {
            1: "Normal Search",
            2: "Vector Search",
            3: "Ranking Search",
            4: "View All Results",
            5: "Quit",
        }
        print("-" * 20)
        for k, v in choices.items():
            print(f"{k}) {v}")
        print("-" * 20, "\n")

        choice = input("Enter choice: ")
        return int(choice if choice.isnumeric() else 0), choices

    def input_query(self) -> str:
        while True:
            query = input("Enter the Search query: ")
            if query:
                return query

            print("Invalid Query")

    def handle(self, *args, **options):
        colums = ["pk", "name", "price", "rank", "description"]
        products = models.QuerySet(model=Product)

        while True:
            os.system("clear")
            choice, choices = self.menu()

            match choice:
                case 1:
                    query = self.input_query()
                    products = Product.objects.filter(
                        models.Q(name__search=query)
                        | models.Q(description__search=query)
                    )

                case 2:
                    products = Product.objects.annotate(
                        search=SearchVector(*list(self.PRODUCT_SEARCH_FIELDS.keys()))
                    ).filter(search=self.input_query())

                case 3:
                    vectors = [
                        SearchVector(
                            field,
                            weight=weight,
                        )
                        for field, weight in self.PRODUCT_SEARCH_FIELDS.items()
                    ]
                    query = SearchQuery(
                        self.input_query(), search_type="websearch", config="english"
                    )
                    weights = self.get_weights()
                    products = (
                        Product.objects.annotate(
                            rank=SearchRank(
                                reduce(lambda v1, v2: v1 + v2, vectors),
                                query,
                                weights=weights,
                            ),
                        )
                        .filter(rank__gte=0.3)
                        .order_by("-rank")
                    )

                case 4:
                    products = Product.objects.all()

                case 5:
                    exit(0)

                case _:
                    self.print_interrupt_message("Invalid Choice")
                    continue

            print(f"{products.count()} products were found.")
            self.print_result(choices[choice], products)
            self.print_result_to_file(products, colums)

            self.print_interrupt_message()
