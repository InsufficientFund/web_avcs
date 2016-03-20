from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50,widget=forms.TextInput(), required=False)
    email = forms.EmailField(required=False)
    weight_file = forms.FileField(required=False)
    video_file = forms.FileField(required=False)