from django.http import HttpResponseRedirect
from django.shortcuts import render

import calendar
from calendar import HTMLCalendar
from datetime import datetime

from .models import User, Policy, Event, PoliticalParty

from .forms import SearchForm

# Create your views here.
def home(request):
    return render(request, 'djangoapp/index.html')

def search(request):
    return render(request, 'djangoapp/search.html')

# Output results of search with filter used
def results(request):
    query = request.GET.get('search')
    filter = request.GET.get('filter1')

    print(f"Filter value: {filter}")

    # Initialize holders for search results
    users = None
    policies = None
    events = None
    political_party = None

    # Use switch statement to determine which filter to use
    match filter:
        case 'policies':
            if query:
                policies = Policy.objects.filter(name__icontains=query)
            else:
                policies = Policy.objects.all()
        case 'events':
            if query:
                events = Event.objects.filter(name__icontains=query)
            else:
                events = Event.objects.all()
        case 'political party':
            if query:
                political_party = PoliticalParty.objects.filter(name__icontains=query)
            else:
                political_party = PoliticalParty.objects.all()
        case _: # Default to full output of every record if no filter is selected
            if query:
                users = User.objects.filter(official__user__firstname__icontains=query)
                policies = Policy.objects.filter(name__icontains=query)
                events = Event.objects.filter(name__icontains=query)
                political_party = PoliticalParty.objects.filter(name__icontains=query)
            else:
                users = User.objects.all()
                policies = Policy.objects.all()
                events = Event.objects.all()
                political_party = PoliticalParty.objects.all()
    
    return render(request, 'djangoapp/results.html', {"users": users,
                                                      "policies": policies,
                                                      "events": events,
                                                      "political_party": political_party,
                                                      "query": query})
    #candidates = Candidate.objects.select_related('official_user')