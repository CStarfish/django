from django import forms

class search_form(forms.Form):
    search = forms.CharField(max_length=100)