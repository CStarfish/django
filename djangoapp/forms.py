from django import forms
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.forms import UserCreationForm

from djangoapp.models import Student, Official, User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=[('general', 'General'),
                 ('student', 'Student'),
                 ('official', 'Official')],
        required=True)
    student_id = forms.CharField(required=False)
    school_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'date_of_birth', 'user_type','password1', 'password2']
    
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

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user_type = self.cleaned_data.get('user_type')
        
        if user_type == 'student':
            user.is_student = True

        if commit:
            user.save()

        # Handle student
        if user.is_student:
            student = Student(
                user=user, 
                student_id=self.cleaned_data.get('student_id'),
                school_name=self.cleaned_data.get('school_name')
            )
            if commit:
                student.save()

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