from django import forms

class FindingRegisterForm(forms.Form):
    tile = forms.CharField(label="title", max_length=100)
    description = forms.CharField(widget=forms.Textarea)