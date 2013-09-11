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
    result = gatherer.getAllCards()
    if result == "CARD_NOT_FOUND":
        return {"status": "error", "message": "Card not found."}
    else:
        return result

def populateDatabase():
    gatherer = CardDatabase()
    result = gatherer.getAllCards()

def searchCard(**data):
    gatherer = CardDatabase()
    result = gatherer.searchCard(**data)
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

    if operation == "populatedatabase":
        return Response(populateDatabase())

    if operation == "searchcard":
        return Response(searchCard(**data))
