from http import HTTPStatus
from typing import Any, Dict, List, Optional, TypedDict

from django.http import JsonResponse


class ResponseType(TypedDict):
    message: Optional[str]


class SuccessResponseType(ResponseType):
    data: Dict[str, Any] | List[Dict[str, Any]]


class FailedResponseType(ResponseType):
    errors: List[Dict[str, Any]] | Dict[str, Any]


def make_success_response(
    data: Dict[str, Any] | List[Dict[str, Any]], message: str
) -> SuccessResponseType:
    responseData = {"data": data}
    if message:
        responseData["message"] = message

    return responseData


def make_failed_response(
    errors: List[Dict[str, Any]] | Dict[str, Any], message: str
) -> FailedResponseType:
    if not errors:
        raise ValueError("Errors must be provided for status >= 400.")

    message = message if message else "Invalid Data."
    return {"errors": errors, "message": message}


def make_response(
    data: Dict[str, Any] | List[Dict[str, Any]] = {},
    errors: List[Dict[str, Any]] | Dict[str, Any] = [],
    message: str = "",
    status: HTTPStatus | int = HTTPStatus.OK.value,
) -> JsonResponse:
    if isinstance(status, HTTPStatus):
        status = status.value

    if status >= 400:
        responseData = make_failed_response(errors, message)
    else:
        responseData = make_success_response(data, message)

    return JsonResponse(data=responseData, status=status, safe=False)
