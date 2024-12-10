from datetime import datetime
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
        widget = forms.TextInput(attrs={"id": 'username'})
    )

    password = forms.CharField(
        required = True,
        widget = forms.PasswordInput(attrs={"id": 'password'})
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
    profile_picture = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    bio = forms.CharField(widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
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
        ('election offices', 'Election Offices'),
        ('polling locations', 'Polling Locations')
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


class PolicyUpdateForm(forms.ModelForm):
    name = forms.CharField()
    desc = forms.TextInput()
    class Meta:
        model = Policy
        fields = ['name', 'desc']


class EventCreationForm(forms.ModelForm):
    name = forms.CharField()
    # location = forms.CharField()
    state = forms.CharField()
    city = forms.CharField()
    street = forms.CharField()
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    desc = forms.TextInput()
    
    class Meta:
        model = Event
        fields = ['name', 'state', 'city', 'street', 'start_date', 'start_time', 'end_date', 'end_time', 'desc']

    def clean(self):
        cleaned_data = super().clean()

        # Clean location data
        state = cleaned_data.get('state')
        city = cleaned_data.get('city')
        street = cleaned_data.get('street')

        # Clean time data
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_date = cleaned_data.get('end_date')
        end_time = cleaned_data.get('end_time')

        if state and city and street:
            cleaned_data['location'] = f"{street}, {city}, {state}"
        else:
            raise forms.ValidationError("Missing location.")

        if start_date and start_time:
            cleaned_data['start'] = datetime.combine(start_date, start_time)
        else:
            raise forms.ValidationError("Missing start date and/or time.")

        if end_date and end_time:
            cleaned_data['end'] = datetime.combine(end_date, end_time)
        else:
            raise forms.ValidationError("Missing end date and/or time.")

        return cleaned_data

    # Ensure getting coordinates location returns a valid address
    def clean_location(self):
        location = self.cleaned_data.get('location')
        mapbox_token = 'pk.eyJ1IjoiY3N0YXJmaXNoIiwiYSI6ImNtM2NobHBpbTF2cGkyaW9sbWgyYjhlYXYifQ.iI1fAgnb4qUJ7J2JmecpYA'

        # Request location data from Mapbox API
        response = requests.get(
            f'https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json',
            params={'access_token': mapbox_token}
        )

        if response.status_code == 200:
            data = response.json()

            # Check if the result count is too vague or ambiguous
            if len(data['features']) > 1:
                raise ValidationError("Location is too vague. Please enter a more precise address.")
            elif len(data['features']) == 0:
                raise ValidationError("Could not find this location. Please enter a valid location.")
        
        return location
    
    def save(self, commit=True):
        # Get the cleaned data
        cleaned_data = self.cleaned_data
        # Create or update the Event object
        event = super().save(commit=False)

        # Assign the location, start, and end values to the model instance
        event.location = cleaned_data.get('location')
        event.start = cleaned_data.get('start')
        event.end = cleaned_data.get('end')

        # Save the event instance
        if commit:
            event.save()

        return event

        
class EventUpdateForm(EventCreationForm):
    name = forms.CharField()
    state = forms.CharField()
    city = forms.CharField()
    street = forms.CharField()
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    desc = forms.TextInput()

    class Meta(EventCreationForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            # Split the location into street, city, and state
            if self.instance.location:
                location_parts = self.instance.location.split(", ")
                if len(location_parts) == 3:
                    self.fields['street'].initial = location_parts[0]
                    self.fields['city'].initial = location_parts[1]
                    self.fields['state'].initial = location_parts[2]

            start_datetime = self.instance.start
            self.fields['start_date'].initial = start_datetime.date()
            self.fields['start_time'].initial = start_datetime.time()
            
            end_datetime = self.instance.end
            self.fields['end_date'].initial = end_datetime.date()
            self.fields['end_time'].initial = end_datetime.time()


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
    state = forms.CharField()
    city = forms.CharField()
    street = forms.CharField()

    class Meta:
        model = PollingLocation
        fields = ['name', 'contact_info', 'location_picture']

        name = forms.CharField()
        location = forms.CharField()
        contact_info = forms.CharField()
        location_picture = forms.ImageField(widget = forms.FileInput(attrs={'class': 'form-control-file'}))

    def clean(self):
        cleaned_data = super().clean()

        state = cleaned_data.get('state')
        city = cleaned_data.get('city')
        street = cleaned_data.get('street')

        if state and city and street:
            cleaned_data['location'] = f"{street}, {city}, {state}"
        else:
            raise forms.ValidationError("Missing location.")

        return cleaned_data

    # Ensure getting coordinates location returns a valid address
    def clean_location(self):
        location = self.cleaned_data.get('location')
        mapbox_token = 'pk.eyJ1IjoiY3N0YXJmaXNoIiwiYSI6ImNtM2NobHBpbTF2cGkyaW9sbWgyYjhlYXYifQ.iI1fAgnb4qUJ7J2JmecpYA'

        # Request location data from Mapbox API
        response = requests.get(
            f'https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json',
            params={'access_token': mapbox_token}
        )

        if response.status_code == 200:
            data = response.json()

            # Check if the result count is too vague or ambiguous
            if len(data['features']) > 1:
                raise ValidationError("Location is too vague. Please enter a more precise address.")
            elif len(data['features']) == 0:
                raise ValidationError("Could not find this location. Please enter a valid location.")
        
        return location
    
    def save(self, commit=True):
        # Get the cleaned data
        cleaned_data = self.cleaned_data
        # Create or update the Event object
        polling_location = super().save(commit=False)

        # Assign the location, start, and end values to the model instance
        polling_location.location = cleaned_data.get('location')

        # Save the event instance
        if commit:
            polling_location.save()

        return polling_location


class PollingLocationUpdateForm(PollingLocationForm):
    state = forms.CharField()
    city = forms.CharField()
    street = forms.CharField()

    class Meta(PollingLocationForm.Meta):
        pass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            # Split the location into street, city, and state
            if self.instance.location:
                location_parts = self.instance.location.split(", ")
                if len(location_parts) == 3:
                    self.fields['street'].initial = location_parts[0]
                    self.fields['city'].initial = location_parts[1]
                    self.fields['state'].initial = location_parts[2]

        
class MessageForm(forms.ModelForm):
    class Meta:
        model = Messages
        fields = ['user2', 'message']