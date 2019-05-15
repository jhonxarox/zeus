from django import forms

class uploadForm(forms.Form):
    file_input = forms.FileInput()