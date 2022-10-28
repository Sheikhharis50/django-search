from django.apps import AppConfig


class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "search"

    def ready(self) -> None:
        from .signals import product_pre_save_actions

        return super().ready()
