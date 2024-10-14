from django.http import HttpResponseRedirect
from django.shortcuts import render

import calendar
from calendar import HTMLCalendar
from datetime import datetime

from .models import Candidate, Policy, Event

from .forms import SearchForm

# Create your views here.
def home(request):
    return render(request, 'djangoapp/index.html')

def search(request):
    return render(request, 'djangoapp/search.html')

def results(request):
    query = request.GET.get('search')
    candidates = None
    policies = None
    events = None

    if query:
        candidates = Candidate.objects.select_related('official__user').filter(official__user__firstname__icontains=query)
        policies = Policy.objects.filter(name__icontains=query)
        events = Event.objects.filter(name__icontains=query)
    else:
        candidates = Candidate.objects.select_related('official__user')
        policies = Policy.objects.all()
        events = Event.objects.all()
    
    return render(request, 'djangoapp/results.html', {"candidates": candidates,
                                                      "policies": policies,
                                                      "events": events})
    #candidates = Candidate.objects.select_related('official_user')