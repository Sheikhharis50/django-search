from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Product
from .utils import prep_product_search_vector_index


@receiver(pre_save, sender=Product)
def product_pre_save_actions(sender, instance: Product, update_fields, **kwargs):
    if not update_fields or (
        update_fields
        and not any([f in update_fields for f in Product.SEARCH_VECTOR_FIELDS])
    ):
        return

    prep_product_search_vector_index(products=[instance], save=False)
