from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm)

from django.core.exceptions import ValidationError

from djangoapp.models import *
from djangoapp.models import PoliticalParty


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=[('general', 'General'),
                 ('student', 'Student'),
                 ('official', 'Official')],
        required=True)
    student_id = forms.CharField(required=False)
    school_name = forms.CharField(required=False)
    POLITICAL_PARTIES = [
        ('', 'Select a party'),
        ('democratic', 'Democratic Party'),
        ('republican', 'Republican Party')
    ]

    political_party = forms.ModelChoiceField(
        queryset = PoliticalParty.objects.all(),
        empty_label = "Select a party",
        required = False
    )
    state = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'date_of_birth', 'political_party', 'user_type','password1', 'password2']
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')

        if user_type == 'student':
            # Validate student-specific fields
            student_id = cleaned_data.get('student_id')
            school_name = cleaned_data.get('school_name')
            if not student_id:
                self.add_error('student_id', 'This field is required for students.')
            if not school_name:
                self.add_error('school_name', 'This field is required for students.')

        if user_type == 'official':
            state = cleaned_data.get('state')
            political_party = cleaned_data.get('political_party')
            if not state:
                self.add_error('state', 'This field is required for officials.')
            if political_party is None:
                self.add_error('political_party', 'Officials must specify a political party.')

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user_type = self.cleaned_data.get('user_type')
        
        if user_type == 'student':
            user.is_student = True
        elif user_type == 'official':
            user.is_official = True

        if commit:
            user.save()

        # Handle student
        if user.is_student:
            student = Student(
                user = user, 
                student_id = self.cleaned_data.get('student_id'),
                school_name = self.cleaned_data.get('school_name')
            )
            if commit:
                student.save()
        # Handle official
        elif user.is_official:
            official = Official(
                user = user, 
                state = self.cleaned_data.get('state')
            )
            if commit:
                official.save()

        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        required = True,
        widget = forms.TextInput(attrs = {"id": 'username'})
    )

    password = forms.CharField(
        required = True,
        widget = forms.TextInput(attrs = {"id": 'password'})
    )


class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    username = forms.CharField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    political_party = forms.ModelChoiceField(
        queryset=PoliticalParty.objects.all(),
        empty_label="None",
        required=False
    )
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'political_party']

    def clean(self):
        cleaned_data = super().clean()
        user = self.instance

        if user.is_official:
            political_party = cleaned_data.get('political_party')

            if political_party is None:
                self.add_error('political_party', 'Officials must specify a political party.')


class UpdateProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(widget = forms.FileInput(attrs={'class': 'form-control-file'}))
    bio = forms.CharField(widget = forms.Textarea(attrs = {'class': 'form-control', 'rows': 5}))
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio']


class SearchForm(forms.Form):
    query = forms.CharField(
        required = False, 
        widget = forms.TextInput(attrs={
            'id': 'search', 
            'placeholder': 'Search for candidates or topics...'
        })
    )
    
    FILTER_CHOICES = [
        ('', 'All'),
        ('events', 'Events'),
        ('policies', 'Policies'),
        ('candidates', 'Candidates'),
    ]
    
    filter1 = forms.ChoiceField(
        choices = FILTER_CHOICES, 
        required = False, 
        widget = forms.Select(attrs={'id': 'filter1'})
    )


class CandidacyForm(forms.ModelForm):
    campaign_name = forms.CharField()
    campaign_details = forms.TextInput()
    class Meta:
        model = Candidate
        fields = ['campaign_name', 'campaign_details']


class PolicyCreationForm(forms.ModelForm):
    name = forms.CharField()
    desc = forms.TextInput()
    class Meta:
        model = Policy
        fields = ['name', 'desc']


class EventCreationForm(forms.ModelForm):
    name = forms.CharField()
    address = forms.CharField()
    start = forms.DateTimeField()
    end = forms.DateTimeField()
    desc = forms.TextInput()
    class Meta:
        model = Event
        fields = ['name', 'location', 'start', 'end', 'desc']


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'desc']

    RATING_NUMBER = [
        (5, '5'),
        (4, '4'),
        (3, '3'),
        (2, '2'),
        (1, '1'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_NUMBER,
        widget=forms.RadioSelect(attrs={'class': 'star-rating'}),
        label="Rating"
    )
    desc = forms.TextInput()


class PollingLocationForm(forms.ModelForm):
    class Meta:
        model = PollingLocation
        fields = ['name', 'location', 'contact_info', 'location_picture']

        name = forms.CharField()
        location = forms.CharField()
        contact_info = forms.CharField()
        location_picture = forms.ImageField(widget = forms.FileInput(attrs={'class': 'form-control-file'}))