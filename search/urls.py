from django.urls import path

from .views import SearchView, SearchWithTypeView

urlpatterns = [
    path("<str:query>/", view=SearchView.as_view()),
    path("<str:query>/<str:type>/", view=SearchWithTypeView.as_view()),
]
