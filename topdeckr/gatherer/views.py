# Create your views here
from django.utils import simplejson
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, Template
from django.http import HttpResponse
from gatherer.api import CardDatabase
from django.views.decorators.csrf import csrf_exempt
from re import escape

@csrf_exempt
def get_card(request):
	if request.is_ajax():
		gatherer = CardDatabase()
		result = gatherer.online_lookup(request.POST['name'])
		if result == "CARD_NOT_FOUND":
			return HttpResponse(simplejson.dumps({"error": "CARD_NOT_FOUND"}), mimetype="application/json")
		else:
			return HttpResponse(simplejson.dumps(result), mimetype="application/json")
	else:
		return HttpResponse(simplejson.dumps("error"), mimetype="application/json")
