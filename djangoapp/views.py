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
    form = SearchForm(request.GET or None)
    results = Candidate.objects.select_related('official__user').prefetch_related('policies', 'events')

    if form.is_valid():
        search_term = form.cleaned_data.get('search')  # Get the search input from the form

        # Filter candidates by name (case-insensitive search)
        if search_term:
            results = results.select_related('official__user').filter(official__user__firstname__icontains=search_term)

        context = {
            'form': form,
            'results': results,  # Pass the filtered results to the template
        }
    return render(request, 'djangoapp/results.html', {"results": results})
    #candidates = Candidate.objects.select_related('official_user')