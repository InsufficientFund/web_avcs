from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50,widget=forms.TextInput())
    file = forms.FileField()