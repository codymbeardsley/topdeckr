# Create your views here
from django.utils import simplejson
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, Template
from django.http import HttpResponse
from gatherer.api import CardDatabase
from django.views.decorators.csrf import csrf_exempt
from re import escape

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

def getCard(**data):
    gatherer = CardDatabase()
    result = gatherer.online_lookup(**data)
    if result == "CARD_NOT_FOUND":
        return {"error": "CARD_NOT_FOUND"}
    else:
        return result

@api_view(['POST'])
def gathererRequest(request, operation):
    data = {}
    try:
        data = request.POST
    except:
        pass

    if operation == "getcard":
        return Response(getCard(**data))

