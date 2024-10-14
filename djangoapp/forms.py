from django import forms

class SearchForm(forms.Form):
    search_query = forms.CharField(max_length=100)
    filter_candidate = forms.BooleanField()
    filter_policy = forms.BooleanField()
    filter_event = forms.BooleanField()
