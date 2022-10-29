import asyncio
import os
from typing import Dict, List, Tuple

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import models
from search.models import Product
from search.services import SearchService
from search.utils import prep_product_search_vector_index


class Command(BaseCommand):
    help = "Search Products"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--index",
            action="store_true",
            help="Index all products first before performing search.",
        )

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

    def handle_options(self, products: models.QuerySet[Product], **options):
        if options.get("index", False):
            prep_product_search_vector_index(products)

    def handle(self, *args, **options):
        colums = ["pk", "name", "price", "rank", "description"]
        service = SearchService()
        products = service.get_products()

        self.handle_options(products, **options)

        while True:
            os.system("clear")
            choice, choices = self.menu()

            match choice:
                case 1:
                    query = self.input_query()
                    products = service.normal_search(query)

                case 2:
                    query = self.input_query()
                    products = service.vector_search(query)

                case 3:
                    query = self.input_query()
                    products = service.ranking_search(query)

                case 4:
                    pass

                case 5:
                    exit(0)

                case _:
                    self.print_interrupt_message("Invalid Choice")
                    continue

            products = asyncio.run(products)
            print(f"{products.count()} products were found.")
            # self.print_result(choices[choice], products)
            self.print_result_to_file(products, colums)

            self.print_interrupt_message()
