# Create your views here
from django.utils import simplejson
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, Template
from django.http import HttpResponse
from gatherer.api import CardDatabase
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_card(request):
	if request.is_ajax():
		gatherer = CardDatabase()
		return HttpResponse(simplejson.dumps(gatherer.online_lookup("r")), mimetype="application/json")
	else:
		return HttpResponse(simplejson.dumps("error"), mimetype="application/json")
