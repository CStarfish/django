from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (PasswordResetView, PasswordChangeView)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

import calendar
from calendar import HTMLCalendar
from datetime import datetime

from django.urls import reverse_lazy

from django.views import View
from django.views.generic import (TemplateView, FormView)

from .models import *
from .models import (User, Profile, Policy, Event, PoliticalParty, Candidate, Candidate, Follow, UserUpdate)

from .forms import *

# Create your views here.
# Displays home page
def HomeView(request):
    # Get current time and filter events where start time is greater than current time
    now = timezone.now()
    events = Event.objects.filter(start__gt=now)

    # Gets a random policy and candidate to feature
    candidate = User.objects.filter(is_candidate=True).order_by('?').first()
    policy = Policy.objects.order_by('?').first()
    return render(request, 'djangoapp/home.html', {"events": events,
                                                   "candidate": candidate,
                                                   "policy": policy
                                                   })


def AboutView(request):
    return render(request, 'djangoapp/index.html')


def About1View(request):
    return render(request, 'djangoapp/jly.html')


def About2View(request):
    return render(request, 'djangoapp/jwong.html')


def About3View(request):
    return render(request, 'djangoapp/erik.html')


def About4View(request):
    return render(request, 'djangoapp/bilguun.html')


def About5View(request):
    return render(request, 'djangoapp/haolongd.html')


def About6View(request):
    return render(request, 'djangoapp/pablo.html')


def About7View(request):
    return render(request, 'djangoapp/madhura.html')


# register page
# Displays register form and sends form data to the RegistrationForm
class RegisterView(FormView):
    template_name = 'djangoapp/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):     
        user = form.save()  
        login(self.request, user)   # Log the user in after registration
        messages.success(self.request, "Successful registration!")
        return redirect('profile', user_id=user.id) # Redirect to the profile page

    def form_invalid(self, form):   
        messages.error(self.request, "Failed registration") 
        return super().form_invalid(form) # Return to the registration page with errors


# login page
# Displays login form and authenticates LoginForm data
class LoginView(FormView):
    template_name = 'djangoapp/login.html' 
    form_class = LoginForm  
   
    # If the form is valid, authenticate the user and log them in
    def form_valid(self, form): 
        user = authenticate(self.request, **form.cleaned_data)  
        if user is not None: 
            login(self.request, user) 
            messages.success(self.request, "Successful login!")
            return redirect('profile', user_id=user.id) 
        else: 
            messages.error(self.request, "Invalid username or password.")
            return self.form_invalid(form)


# logout
def LogoutView(request):
    logout(request)  # Clears session
    return redirect('home')


# Password reset
class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'djangoapp/password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Find the user by email
        email = form.cleaned_data.get("email")
        users = User.objects.filter(email=email)
        
        if users.exists():
            user = users.first()
            # Generate token and UID for the user
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Redirect to PasswordResetConfirmView with UID and token
            return redirect(reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))
        else:
            # No user found
            messages.error(self.request, "Invalid Email.")
            return super().form_invalid(form)
        

class PasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):      
    template_name = 'djangoapp/password_change.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('home')


# profile page
# Displays and allows updates to user profile through UpdateUserForm and UpdateProfileForm
class ProfileView(LoginRequiredMixin, View):
    template_name = 'djangoapp/profile.html'

    # GET request to display the profile page
    def get(self, request, user_id):
        if not request.user.is_authenticated:
            return redirect('djangoapp/login.html')
          
        user = get_object_or_404(User, pk=user_id)
        profile = get_object_or_404(Profile, user=user)
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=profile)
        return render(request, self.template_name, {
            'user': user,
            'user_form': user_form,
            'profile_form': profile_form
        })

    # POST request to update the profile page
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


# Search engine logic
# Displays search results based on user input and sends to results.html
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
        election_offices = None
        polling_locations = None

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
                    users = User.objects.filter(is_candidate=True, first_name__icontains=query)
                else:
                    users = User.objects.filter(is_candidate=True)
            case 'election offices':
                if query:
                    election_offices = ElectionOffice.objects.filter(location__icontains=query)
                else:
                    election_offices = ElectionOffice.objects.all()
            case 'polling locations':
                if query:
                    polling_locations = PollingLocation.objects.filter(location__icontains=query)
                else:
                    polling_locations = PollingLocation.objects.all()
            case _: # Default to full output of every record if no filter is selected
                if query:
                    users = User.objects.filter(first_name__icontains=query)
                    policies = Policy.objects.filter(name__icontains=query)
                    events = Event.objects.filter(name__icontains=query)
                    election_offices = ElectionOffice.objects.filter(location__icontains=query)
                    polling_locations = PollingLocation.objects.filter(location__icontains=query)
                else:
                    users = User.objects.all()
                    policies = Policy.objects.all()
                    events = Event.objects.all()
                    election_offices = ElectionOffice.objects.all()
                    polling_locations = PollingLocation.objects.filter(location__icontains=query)

        return render(self.request, self.template_name, {
            "users": users,
            "policies": policies,
            "events": events,
            "election_offices": election_offices,
            "polling_locations": polling_locations,
            "query": query
        })


# Handlers for candidacy, policy, and event creation
# Display forms for creating candidacies, policies, and events
# then sends forms for page generation

# Candidacy creation
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
    
# Policy creation
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

        # Store policy id for later use when rerouting url
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
    
# Event creation
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


'''
View for viewing user profiles, displays all information if possible, including information
regarding different user types and ratings for that user.
'''
class ProfilePageView(View):
    form_class = RatingForm
    template_name = 'djangoapp/profile_page.html'

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        candidate = None
        official = None
        student = None
        policies = None
        events = None
        ratings = None

        rating_form = RatingForm()

        if(user.is_candidate):
            candidate = get_object_or_404(Candidate, user_id=user_id)
            ratings = Rating.objects.filter(candidate__user_id=user_id)
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
            'events': events,
            'ratings': ratings,
            'rating_form': rating_form,
            'current_user': request.user
        })
        
    # Changes post to first double check if user being rated is candidate and if user rating is from another user
    # Probably not necessary but insurance check
    def post(self, request, user_id):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to leave a rating.")
            return self.get(request, user_id)
    
        user = get_object_or_404(User, id=user_id)

        if user.is_candidate and request.user != user:
            candidate = Candidate.objects.filter(user_id=user_id).first()
            form = self.form_class(request.POST)
            if form.is_valid():
                return self.form_valid(form, candidate)
        
        messages.error(self.request, "You are either trying to rate yourself or a non-candidate.")
        return self.get(request, user_id)
    
    def form_valid(self, form, candidate):
        rating = form.save(commit=False)
        rating.user = self.request.user
        rating.candidate = candidate
        rating.save()

        return redirect('profile_page', user_id=candidate.user_id)
    

def ElectionOfficeView(request, user_id):
    election_office = get_object_or_404(ElectionOffice, user_id=user_id)
    return render(request, 'djangoapp/election_office.html', {"election_office": election_office})


'''
View for creating Polling locations, only accessible by officials associated with election offices
This can be achieve by adding officials to Election Office in admin and approving them
'''
class PollingCreationView(LoginRequiredMixin, FormView):
    form_class = PollingLocationForm
    template_name = 'djangoapp/polling_creation.html'

    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user is allowed to access election office content
        if not hasattr(request.user, 'is_election_office'):
            messages.error(request, "You do not have permission to access this page.")
            return redirect('profile') 
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        polling_location = form.save(commit=False)

        office = ElectionOffice.objects.get(user_id=self.request.user.id)
        polling_location.office = office
        polling_location.save()

        self.polling_location_id = polling_location.polling_location_id

        messages.success(self.request, "The polling location has been posted.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with the polling location information.")
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('polling_location', args=[self.polling_location_id])
    

def PollingLocationView(request, polling_location_id):
    polling_location = get_object_or_404(PollingLocation, polling_location_id=polling_location_id)
    return render(request, 'djangoapp/polling_location.html', {'polling_location': polling_location})


# View to follow a candidate or event
def FollowView(request, candidate_id=None, event_id=None):
    if candidate_id:
        candidate = get_object_or_404(Candidate, pk=candidate_id)
        Follow.objects.get_or_create(user=request.user, candidate=candidate)
        messages.success(request, f"You are now following {candidate}.")
    elif event_id:
        event = get_object_or_404(Event, pk=event_id)
        Follow.objects.get_or_create(user=request.user, event=event)
        messages.success(request, f"You are now following {event}.")
        
    return redirect('profile', user_id=request.user);

    # View to unfollow
def UnfollowView(request, candidate_id=None, event_id=None):
    if candidate_id:
        candidate = get_object_or_404(Candidate, pk=candidate_id)
        Follow.objects.filter(user=request.user, candidate=candidate).delete()
        messages.success(request, f"You have unfollowed {candidate}.")
    elif event_id:
        event = get_object_or_404(Event, pk=event_id)
        Follow.objects.filter(user=request.user, event=event)
        messages.success(request, f"You have unfollowed {event}.")
    return redirect('profile', user_id=request.user.id)