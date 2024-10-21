from django import forms
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
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

class SearchForm(forms.Form):
    search = forms.CharField(
        required = False, 
        widget = forms.TextInput(attrs = {
            'id': 'search', 
            'placeholder': 'Search for candidates or topics...'
        })
    )
    
    FILTER_CHOICES = [
        ('', 'All'),
        ('events', 'Events'),
        ('policies', 'Policies'),
        ('political party', 'Political Party'),
    ]
    
    filter1 = forms.ChoiceField(
        choices = FILTER_CHOICES, 
        required = False, 
        widget = forms.Select(attrs = {'id': 'filter1'})
    )