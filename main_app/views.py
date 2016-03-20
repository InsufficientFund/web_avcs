from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from django.conf import settings

def index(request):
    form = UploadFileForm()
    return render(request, 'main_app/index.html',{'form':form})

def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.POST, request.FILES, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['video_file'])
            handle_uploaded_file(request.FILES['weight_file'])
            return HttpResponse("success")
        else:
        	return HttpResponse("invalid")
    else:
        form = UploadFileForm()
    	return HttpResponse("failed")
    # return render(request, 'upload.html', {'form': form})


    # return HttpResponse("Hello, world. You're at the polls index.")
# Create your views here.

def handle_uploaded_file(f):
    with open(settings.MEDIA_ROOT+"upload/"+f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)