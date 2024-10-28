from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

import calendar
from calendar import HTMLCalendar
from datetime import datetime

from .models import (User, Profile, Policy, Event, PoliticalParty)

from .forms import (SearchForm, LoginForm, RegistrationForm, UpdateUserForm, UpdateProfileForm)

# Create your views here.
def home_view(request):
    return render(request, 'djangoapp/home.html')


def about_view(request):
    return render(request, 'djangoapp/index.html')


def register_view(request):
    #if request.user.is_authenticated:
        #return redirect('profile', user_id = request.user.id)
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Successful registration!")
            return redirect('profile', user_id = user.id)
        else:
            print(form.errors)
            messages.error(request, "Failed registration")
    else:
        form = RegistrationForm()
    
    return render(request, 'djangoapp/register.html', {'form': form})


#login page
def login_view(request):
    # if the user is already logged in, redirect to their profile page
    # if request.user.is_authenticated:
        #return redirect('profile', user_id = request.user.id)

    # Check if request is a post, if it's a get, that means it's user's first time entering login page
    if request.method == 'POST':
        form = LoginForm(request, data = request.POST)
        # check if inputs are valid
        if form.is_valid():
            user = authenticate(request, **form.cleaned_data)
            # If user exists
            if user is not None:
                login(request, user) # login as user
                messages.success(request, "Successful login!")
                return redirect('profile', user_id = user.id)  # Redirect to profile page
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'djangoapp/login.html', {'form': form})


#logout
def logout_view(request):
    logout(request)  # Clears session
    return redirect('home')


#profile page
def profile_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)  # get user_id, otherwise 404
    profile = get_object_or_404(Profile, user=user)
    # Handle user changing account information
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance = request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance = profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Successful profile update.')
            return redirect('profile', user_id = user.id)
        else:
            print(user_form.errors)
            messages.error(request, "Failed profile update.")
    else:
        user_form = UpdateUserForm()
        profile_form = UpdateProfileForm()
    return render(request, 'djangoapp/profile.html', {
                                                    'user': user,
                                                    'user_form': user_form,
                                                    'profile_form': profile_form
                                                    })


#Search bar page
def search_view(request):
    form = SearchForm(request.GET or None)
    if form.is_valid():
        query = form.cleaned_data['query']
        filter1 = form.cleaned_data['filter1']

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
        return render(request, 'djangoapp/results.html', {'form': form,
                                                         "users": users,
                                                         "policies": policies,
                                                         "events": events,
                                                         "political_party": political_party,
                                                         "query": query
                                                        })


# Output results of search with filter used
def results_view(request):
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
    
def policy_detail(request, policy_id):
    policy = get_object_or_404(Policy, policy_id=policy_id)
    return render(request, 'djangoapp/policy_detail.html', {'policy' : policy})