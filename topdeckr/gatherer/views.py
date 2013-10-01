# Create your views here
from gatherer.api import CardDatabase
from gatherer.search import search_cards
from rest_framework.response import Response
from rest_framework.decorators import api_view


def api_get_card(**data):
    gatherer = CardDatabase()
    return gatherer.get_card(**data)


def api_populate_database():
    gatherer = CardDatabase()
    return gatherer.get_all_cards()


def api_search_cards(**data):
    result = search_cards(**data)
    return result


@api_view(['POST'])
def gatherer_request(request, operation):
    data = request.POST

    if operation == "get_card":
        return Response(api_get_card(**data))

    elif operation == "populate_database":
        return Response(api_populate_database())

    elif operation == "search_cards":
        return Response(api_search_cards(**data))
