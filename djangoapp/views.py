from django.shortcuts import render
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Candidate

# Create your views here.
def index(request):
    return render(request, 'djangoapp/index.html')

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
    # GET search query adn filters
    query = request.GET.get('query', '')
    location = request.GET.get('location', '')
    party = request.GET.get('party', '')
    experience = request.GET.get('experience', '')
    topics = request.GET.get('topics', '')
    
    # candidates
    candidates = Candidate.objects.select_related('official_user')
    
    # apply filters
    if query:
        candidates = candidates.filter(official_user_firstname_icontains=query)
        
    if location:
        candidates = candidates.filter(official_state_iexact=location)
        
    if party: 
        candidates = candidates.filter(official_user_political_party_name_iexact=party)
    
    # Need to figure out how to filter experience
    if experience:
        pass
    
    if topics:
        candidates = candidates.filter(policies_name_icontains=topics)
        
    return render(request, 'djangoapp/results.html',{'results' : candidates})
    #results = User.objects.all()  # Query all users
    #results = Candidate.objects.select_related('official__user').all()  # Query all users that are candidates
    #return render(request, 'djangoapp/results.html', {'results': results})