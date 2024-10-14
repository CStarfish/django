from django.shortcuts import render
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Candidate

# Create your views here.
def index(request):
    return render(request, 'index.html')

def search(request):
    query = request.POST.get('query', '')
    location = request.POST.get('location', '')

    results = Candidate.objects.all()

    if query:
        results = results.filter(name_icontains=query)
    if location:
        results = results.filter(location_iexact=location)
    return render(request, 'djangoapp/search.html', {'results': results, 'query': query, 'location': location})

def results(request):
    #results = User.objects.all()  # Query all users
    results = Candidate.objects.select_related('official__user').all()  # Query all users that are candidates
    return render(request, 'djangoapp/results.html', {'results': results})