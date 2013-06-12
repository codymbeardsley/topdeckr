# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, Template

def index(request):
	return render_to_response("common/common_index.html", {}, context_instance=RequestContext(request))
	
