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
from .models import (User, Profile, Policy, Event, PoliticalParty, Candidate, Candidate)

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
            error_messages = []
            if not user_form.is_valid():
                error_messages.append("User form has errors.")
            if not profile_form.is_valid():
                error_messages.append("Profile form has errors.")
            messages.error(request, " ".join(error_messages))
            return render(request, self.template_name, {
                'user': user,
                'user_form': user_form,
                'profile_form': profile_form
            })


#Search engine logic
class SearchView(FormView):
    template_name = 'djangoapp/results.html'
    form_class = SearchForm

    def get(self, request):
        query = self.request.GET.get('query')
        filter1 = self.request.GET.get('filter1')

        print(f"Query: {query}")

        users = None
        policies = None
        events = None
        match filter1:
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
            case 'candidates':
                if query:
                    users = User.objects.filter(is_candidate=True)
                else:
                    users = User.objects.filter(is_candidate=True)
            case _: # Default to full output of every record if no filter is selected
                if query:
                    users = User.objects.filter(first_name__icontains=query)
                    policies = Policy.objects.filter(name__icontains=query)
                    events = Event.objects.filter(name__icontains=query)
                else:
                    users = User.objects.all()
                    policies = Policy.objects.all()
                    events = Event.objects.all()

        return render(self.request, self.template_name, {
            "users": users,
            "policies": policies,
            "events": events,
            "query": query
        })


# Output results of search with filter used
# CURRENTLY UNUSED
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
        case 'candidate':
            if query:
                users = User.objects.filter(is_candidate=True)
            else:
                users = User.objects.all()
        case _: # Default to full output of every record if no filter is selected
            if query:
                users = User.objects.filter(official__user__firstname__icontains=query)
                policies = Policy.objects.filter(name__icontains=query)
                events = Event.objects.filter(name__icontains=query)
            else:
                users = User.objects.all()
                policies = Policy.objects.all()
                events = Event.objects.all()
    
    return render(request, 'djangoapp/results.html', {"users": users,
                                                      "policies": policies,
                                                      "events": events,
                                                      "query": query})
    #candidates = Candidate.objects.select_related('official_user')


class CandidacyView(LoginRequiredMixin, FormView):
    template_name = 'djangoapp/candidacy.html'
    form_class = CandidacyForm

    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user is an official
        if not hasattr(request.user, 'is_official'):
            messages.error(request, "You do not have permission to access this page.")
            return redirect('profile') 
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        candidacy = form.save(commit=False)

        official = Official.objects.get(user=self.request.user)
        candidacy.user = official
        candidacy.save()
        messages.success(self.request, "Your candidacy application has been submitted for approval.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting your application.")
        return super().form_invalid(form)
    
    def get_success_url(self):
        # Use the user id from the request to construct the success URL
        user_id = self.request.user.id
        return reverse_lazy('profile', args=[user_id])
    

class PolicyCreationView(LoginRequiredMixin, FormView):
    template_name = 'djangoapp/policy_creation.html'
    form_class = PolicyCreationForm

    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user is an official
        if not hasattr(request.user, 'is_official'):
            messages.error(request, "You do not have permission to access this page.")
            return redirect('profile') 
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        policy = form.save(commit=False)

        official = Official.objects.get(user=self.request.user)
        policy.official = official
        policy.save()

        # store policy id for later use when rerouting url
        self.policy_id = policy.policy_id

        messages.success(self.request, "Your policy has been posted.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error posting your policy.")
        return super().form_invalid(form)
    
    def get_success_url(self):
        if hasattr(self, 'policy_id'):
            return reverse_lazy('policy_page', args=[self.policy_id])
        return reverse_lazy('home')
    

class EventCreationView(LoginRequiredMixin, FormView):
    template_name = 'djangoapp/event_creation.html'
    form_class = EventCreationForm

    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user is an official
        if not hasattr(request.user, 'is_official'):
            messages.error(request, "You do not have permission to access this page.")
            return redirect('profile') 
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        event = form.save(commit=False)

        official = Official.objects.get(user=self.request.user)
        event.official = official
        event.save()

        self.event_id = event.event_id

        messages.success(self.request, "Your event has been posted.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error posting your event.")
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('event_page', args=[self.event_id])


def PolicyPageView(request, policy_id):
    policy = get_object_or_404(Policy, policy_id=policy_id)
    return render(request, 'djangoapp/policy_page.html', {'policy': policy})

def EventPageView(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    return render(request, 'djangoapp/event_page.html', {'event': event})


def ProfilePageView(request, user_id):
    user = get_object_or_404(User, id=user_id)
    candidate = None
    official = None
    student = None
    policies = None
    events = None

    if(user.is_candidate):
        candidate = get_object_or_404(Candidate, user_id=user_id)
    if(user.is_official):
        official = get_object_or_404(Official, user_id=user_id)
        policies = Policy.objects.filter(official__user__id=user_id)
        events = Event.objects.filter(official__user__id=user_id)
    if(user.is_student):
        student = get_object_or_404(Student, user_id=user_id)
        

    return render(request, 'djangoapp/profile_page.html',{
        'user' : user,
        'candidate' : candidate,
        'official': official,
        'student': student,
        'policies': policies,
        'events': events
    })