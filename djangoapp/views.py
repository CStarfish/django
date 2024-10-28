from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin

import calendar
from calendar import HTMLCalendar
from datetime import datetime

from django.urls import reverse_lazy

from django.views import View
from django.views.generic import TemplateView, FormView

from .models import *
from .models import (User, Profile, Policy, Event, PoliticalParty, Candidate)

from .forms import *

# Create your views here.
def HomeView(request):
    return render(request, 'djangoapp/home.html')


def AboutView(request):
    return render(request, 'djangoapp/index.html')


class RegisterView(FormView):
    template_name = 'djangoapp/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Successful registration!")
        return redirect('profile', user_id=user.id)

    def form_invalid(self, form):
        messages.error(self.request, "Failed registration")
        return super().form_invalid(form)


#login page
class LoginView(FormView):
    template_name = 'djangoapp/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        user = authenticate(self.request, **form.cleaned_data)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, "Successful login!")
            return redirect('profile', user_id=user.id)
        else:
            messages.error(self.request, "Invalid username or password.")
            return self.form_invalid(form)


#logout
def LogoutView(request):
    logout(request)  # Clears session
    return redirect('home')


#Password reset
class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')


#profile page
class ProfileView(LoginRequiredMixin, View):
    template_name = 'djangoapp/profile.html'

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        profile = get_object_or_404(Profile, user=user)
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=profile)
        return render(request, self.template_name, {
            'user': user,
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        profile = get_object_or_404(Profile, user=user)
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Successful profile update.')
            return redirect('profile', user_id=user.id)
        else:
            messages.error(request, "Failed profile update.")
            return render(request, self.template_name, {
                'user': user,
                'user_form': user_form,
                'profile_form': profile_form
            })


#Search bar page

class SearchView(FormView):
    template_name = 'djangoapp/results.html'
    form_class = SearchForm

    def form_valid(self, form):
        query = form.cleaned_data.get('query')
        filter1 = form.cleaned_data.get('filter1')

        users = None
        policies = None
        events = None
        political_party = None
        match filter1:
            case 'policies':
                policies = Policy.objects.filter(name__icontains=query) if query else Policy.objects.all()
            case 'events':
                events = Event.objects.filter(name__icontains=query) if query else Event.objects.all()
            case 'political party':
                political_party = PoliticalParty.objects.filter(name__icontains=query) if query else PoliticalParty.objects.all()
            case _:
                users = User.objects.filter(official__user__firstname__icontains=query) if query else User.objects.all()
                policies = Policy.objects.filter(name__icontains=query) if query else Policy.objects.all()
                events = Event.objects.filter(name__icontains=query) if query else Event.objects.all()
                political_party = PoliticalParty.objects.filter(name__icontains=query) if query else PoliticalParty.objects.all()

        return render(self.request, self.template_name, {
            "form": form,
            "users": users,
            "policies": policies,
            "events": events,
            "political_party": political_party,
            "query": query
        })


# Output results of search with filter used
def ResultsView(request):
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


class CandidacyView(LoginRequiredMixin, FormView):
    template_name = 'djangoapp/candidacy.html'
    form_class = CandidacyForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        candidacy = form.save(commit=False)
        candidacy.official.user = self.request.user
        candidacy.save()
        messages.success(self.request, "Your candidacy application has been submitted for approval.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting your application.")
        return super().form_invalid(form)
    
def policy_detail(request, policy_id):
    policy = get_object_or_404(Policy, policy_id=policy_id)
    return render(request, 'djangoapp/policy_detail.html', {'policy' : policy})

def candidate_detail(request, user_id):
    candidate = get_object_or_404(Candidate, user_id=user_id)
    policies = Policy.objects.filter(candidate=candidate)
    events = Event.objects.filter(candidate=candidate)
    
    return render(request, 'djangoapp/candidate_detail.html',{
        'candidate' : candidate,
        'policies' : policies,
        'events' : events
    })