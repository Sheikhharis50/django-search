from datetime import datetime

from core.response import make_response
from core.views import BaseAsyncView
from django.http.request import HttpRequest

from .services import SearchService


class SearchView(BaseAsyncView):
    async def with_time(self, method, *args, **kwargs):
        start_time = datetime.now()
        result = await method(*args, **kwargs) if callable(method) else []
        return {
            "time_taken": f"{(datetime.now()-start_time).total_seconds():.4f} secs.",
            "records": len(result),
            "result": result,
        }

    async def get(self, request: HttpRequest, query: str = ""):
        service = SearchService()
        return make_response(
            {
                "normal_search": await self.with_time(service.anormal_search, query),
                "vector_search": await self.with_time(service.avector_search, query),
                "ranking_search": await self.with_time(service.aranking_search, query),
            }
        )


class SearchWithTypeView(SearchView):
    async def get(self, request: HttpRequest, query: str = "", type: str = ""):
        service = SearchService()
        method = getattr(service, f"a{type}_search", None)
        result = await self.with_time(None)

        if method and callable(method):
            result = await self.with_time(method, query)

        return make_response(result)
