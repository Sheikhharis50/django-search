from django.urls import path

from .views import SearchView

urlpatterns = [
    path("<str:query>/", view=SearchView.as_view()),
]
