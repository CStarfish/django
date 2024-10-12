from django.shortcuts import render
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Candidate

# Create your views here.

def results(request):
    #results = User.objects.all()  # Query all users
    results = Candidate.objects.select_related('official__user').all()  # Query all users that are candidates
    return render(request, 'djangoapp/results.html', {'results': results})