from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UploadFileForm
from django.conf import settings
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import cv2
import json
import time
from AVCS import AVCS
from lbp_feature import lbp_feature
from neural_net import neural_net
from models import CarsModel
from models import ProgressModel
from models import ResultModel
from models import StateModel
from django.contrib.auth.models import User
from save_db import save_result
import glob
import re
import csv
import os
import uuid
import requests
from datetime import timedelta
from django.contrib.auth.models import User
from lda import LDA


def index(request):
    form = UploadFileForm()
    user_count = User.objects.filter(username='admin').count()
    if user_count == 0:
        user = User(username='admin', email='')
        user.set_password('train_admin')
        user.save()
    state = StateModel.objects.filter(state_name='lock_model').count()
    if state == 0:
        db = StateModel(state_name='lock_model', status=0)
        db.save()
    return render(request, 'main_app/index.html', {'form': form})


def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = handle_uploaded_file(request.FILES['file'])
            result_name = filename[:filename.find('.avi')] + '.csv'
            upload_name = request.FILES['file'].name
            save_result(result_name, upload_name, '')
            return HttpResponse(filename)
        else:
            return HttpResponse("Invalid")
    else:
        return HttpResponse("failed")


def handle_uploaded_file(f):
    ext = f.name.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    with open(settings.MEDIA_ROOT+"upload/"+filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return filename


@login_required(login_url='/main/login/')
def train_page(request):
    if request.method == 'GET':
        form = UploadFileForm()
        return render(request, 'main_app/train_page.html',  {'form': form})


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]


def upload_train(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = handle_uploaded_train(request.FILES['file'])
            result_name = filename[:filename.find('.avi')] + '.csv'
            upload_name = request.FILES['file'].name
            save_result(result_name, upload_name, '')
            return HttpResponse(filename)
        else:
            return HttpResponse("Invalid")
    else:
        return HttpResponse("failed")


def handle_uploaded_train(f):
    ext = f.name.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    with open(settings.STATICFILES_DIRS[0]+'main_app/media/train_video/'+filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return filename


def select_video(request):
    if request.is_ajax():
        if request.method == 'GET':
            filename = request.GET['video_name']
            counter = AVCS()
            counter.readVideo(settings.STATICFILES_DIRS[0]+'main_app/media/train_video/'+filename, filename)
            frame = counter.sampleImage()
            frame_name = filename[:filename.find('.avi')] + '.png'
            write_path = settings.STATICFILES_DIRS[0]+'main_app/media/train_image/sample/'+frame_name
            cv2.imwrite(write_path, frame)
            return HttpResponse('train_image/sample/'+frame_name)


def get_train_frame(request):
    if request.is_ajax():
        if request.method == 'GET':
            filename = request.GET['video_name']
            current_frame = request.GET['current_frame']
            counter = AVCS()
            counter.readVideo(settings.STATICFILES_DIRS[0]+'main_app/media/train_video/'+filename, filename)
            frame = counter.sampleImage(int(current_frame)+100)
            frame_name = filename[:filename.find('.avi')] + '.png'
            write_path = settings.STATICFILES_DIRS[0]+'main_app/media/train_image/sample/'+frame_name
            cv2.imwrite(write_path, frame)
            current_milli_time = lambda: int(round(time.time() * 1000))
            return HttpResponse('train_image/sample/'+frame_name + '?' + str(current_milli_time()))


def get_predict_frame(request):
    if request.is_ajax():
        if request.method == 'GET':
            filename = request.GET['video_name']
            current_frame = request.GET['current_frame']
            counter = AVCS()
            counter.readVideo(settings.MEDIA_ROOT+"upload/"+filename, filename)
            frame = counter.sampleImage(int(current_frame)+100)
            frame_name = filename[:filename.find('.avi')] + '.png'
            write_path = settings.STATICFILES_DIRS[0]+'main_app/media/sample_image/'+frame_name
            print write_path
            cv2.imwrite(write_path, frame)
            current_milli_time = lambda: int(round(time.time() * 1000))
            return HttpResponse('sample_image/'+frame_name + '?' + str(current_milli_time()))


def detect(request):
    if request.is_ajax():
        if request.method == 'POST':
            json_data = json.loads(request.body)
            print json_data
            counter = AVCS()
            video_path = settings.STATICFILES_DIRS[0]+'main_app/media/train_video/' + json_data['video_name']
            print video_path
            counter.readVideo(video_path, json_data['video_name'])
            # counter.addLane((131, 142), (203, 142), (123, 245), (213, 245))
            # counter.addLane((205, 142), (275, 142), (215, 245), (316, 245))
            # counter.addLane((155, 182), (225, 182), (123, 285), (232, 285))
            # counter.addLane((227, 182), (302, 182), (234, 285), (356, 285))
            lane_data = json.loads(json_data['data'])
            for lane in lane_data:
                up_left = tuple(map(int,lane["up_left"]))
                up_right = tuple(map(int,lane["up_right"]))
                low_left = tuple(map(int,lane["low_left"]))
                low_right = tuple(map(int,lane["low_right"]))
                counter.addLane(up_left, up_right, low_left, low_right)
            start_time = time.time()
            counter.run(mode='train', cntStatus=False, showVid=False)
            elapsed_time = time.time() - start_time
            print elapsed_time

            listFile = glob.glob(settings.STATICFILES_DIRS[0]+'main_app/media/train_image/*.png')
            listFile.sort(key=natural_keys)
            html = '<form class="form-horizontal" action="/main/train/" method="post" id="select_form">'
            for car_file in listFile:
                car_image = car_file[car_file.find('/static'):]
                car_name = car_file[car_file.find('car'):]
                current_milli_time = lambda: int(round(time.time() * 1000))
                html += '<div><input type="text" size="3" name="' + \
                        car_name + '"> <img src="' + \
                        car_image + '?' + str(current_milli_time()) + '"></div><br>'
            html += '</form>'

            return HttpResponse(html)


def improve_data(request):
    if request.is_ajax():
        if request.method == 'POST':
            selected_data = json.loads(request.body)
            lbp = lbp_feature()
            path = settings.STATICFILES_DIRS[0]+'main_app/media/train_image/'
            answer = []
            feature_list = []
            for data in selected_data:
                if data['value'] != '':
                    file_name = path + data['name']
                    image = cv2.imread(file_name)
                    height, width, channels = image.shape
                    size_data = [height/100.0, width/100.0, height * width/10000.0]
                    resize_image = cv2.resize(image, (64, 64))
                    lbp.read_image(resize_image)
                    feature = lbp.extract_feature(size_data[0], size_data[1], size_data[2], int(data['value']))
                    feature_list.append(feature)
            with open(settings.STATICFILES_DIRS[0]+'main_app/media/train_data.csv', 'a') as fp:
                a = csv.writer(fp, delimiter=',')
                a.writerows(feature_list)
            fp.close()
            file_list = glob.glob(settings.STATICFILES_DIRS[0]+'main_app/media/train_image/*.png')
            for f in file_list:
                os.remove(f)
            return HttpResponse('OK')


def train(request):
    if request.is_ajax():
        if request.method == 'GET':
            print 'train func'
            db = StateModel(state_name='lock_model', status=1)
            db.save()

            # neural_network = neural_net(75, 3)
            # neural_network.create_struct(150)
            file_train = settings.STATICFILES_DIRS[0]+'main_app/media/train_data.csv'

            lda = LDA(75, 3)
            # neural_network.data_input(feature_list, answer, "train")
            # neural_network.file_input(file_train)
            lda.file_input(file_train)
            # neural_network.file_input(file_test, type_set='test')
            # test_data, test_answer = neural_network.get_test_data()
            # neural_network.training(5000)
            # neural_network.save_model(settings.STATICFILES_DIRS[0])
            lda.training()
            lda.save_model(settings.STATICFILES_DIRS[0])
            # print neural_network.predict(test_data[0])
            # print test_answer[0]
            db = StateModel(state_name='lock_model', status=0)
            db.save()
            return HttpResponse('OK')


def predict_page(request):
    if request.method == 'GET':
        state = StateModel.objects.get(pk='lock_model')
        if not state.status:
            form = UploadFileForm()
            return render(request, 'main_app/predict_page.html',  {'form': form})
        else:
            return render(request, 'main_app/construct.html')


def get_sample_frame(request):
    if request.is_ajax():
        if request.method == 'GET':
            filename = request.GET['video_name']
            counter = AVCS()
            counter.readVideo(settings.MEDIA_ROOT+"upload/"+filename, filename)
            frame = counter.sampleImage()
            frame_name = filename[:filename.find('.avi')] + '.png'
            write_path = settings.STATICFILES_DIRS[0]+'main_app/media/sample_image/'+frame_name
            print write_path
            cv2.imwrite(write_path, frame)
            return HttpResponse('sample_image/'+frame_name)


def predict(request):
    if request.is_ajax():
        if request.method == 'POST':
            json_data = json.loads(request.body)
            print json_data
            video_path = settings.MEDIA_ROOT+'upload/' + json_data['video_name']
            print video_path
            lane_data = json.loads(json_data['data'])
            apply_count(json_data['email'], json_data['video_name'], lane_data)
            return HttpResponse('OK_OK')


def apply_count(dest, file_name, lane_data):
    counter = AVCS()
    video_path = settings.MEDIA_ROOT+'upload/' + file_name
    result_name = file_name[:file_name.find('.avi')] + '.csv'
    counter.readVideo(video_path, file_name)
    for lane in lane_data:
        up_left = tuple(map(int,lane["up_left"]))
        up_right = tuple(map(int,lane["up_right"]))
        low_left = tuple(map(int,lane["low_left"]))
        low_right = tuple(map(int,lane["low_right"]))
        counter.addLane(up_left, up_right, low_left, low_right)
    counter.run(mode='predict', cntStatus=False, showVid=False)
    result_type = ['truck', 'passenger car', 'bike']
    raw_feature = CarsModel.objects.filter(file_name=file_name).values_list('frame', 'car_type')
    feature_list = [[x[0], result_type[int(x[1])]] for x in raw_feature]
    with open(settings.MEDIA_ROOT+"result_data/"+result_name, 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(feature_list)
    fp.close()
    ResultModel.objects.filter(pk=result_name).update(email=dest)

    send_mail(dest, file_name)
    return 0


def get_detect_status(request):
    if request.method == 'GET':
        all_obj = CarsModel.objects.all()
        # return_str = [str(obj) for obj in all_obj.values()]
        return_str = serializers.serialize("json", CarsModel.objects.all())
        return HttpResponse(return_str)


def get_graph_data(request):
    if request.method == 'GET':
        file_name = request.GET.get('video_name')
        small_type_count = CarsModel.objects.filter(car_type='2', file_name=file_name).count()
        medium_type_count = CarsModel.objects.filter(car_type='1', file_name=file_name).count()
        large_type_count = CarsModel.objects.filter(car_type='0', file_name=file_name).count()
        return_obj = {
            's': small_type_count,
            'm': medium_type_count,
            'l': large_type_count,
        }

        return HttpResponse(json.dumps(return_obj))


def get_line_data(request):
    if request.method == 'GET':
        file_name = request.GET.get('video_name')
        max_frame = int(request.GET.get('max_frame'))
        return_obj = []

        small_type_cars = CarsModel.objects.filter(car_type='2', file_name=file_name)
        medium_type_cars = CarsModel.objects.filter(car_type='1', file_name=file_name)
        large_type_cars = CarsModel.objects.filter(car_type='0', file_name=file_name)

        for i in range(0, 10):
            round_result = {
                's': 0,
                'm': 0,
                'l': 0
            }
            loop_min_frame = max_frame*(i*10)/100
            loop_max_frame = (max_frame*((i+1)*10)/100)
            # frame_interval = (loop_min_frame, loop_max_frame)
            round_result['s'] = small_type_cars.filter(frame__gte=loop_min_frame).filter(frame__lt=loop_max_frame).count()
            round_result['m'] = medium_type_cars.filter(frame__gte=loop_min_frame).filter(frame__lt=loop_max_frame).count()
            round_result['l'] = large_type_cars.filter(frame__gte=loop_min_frame).filter(frame__lt=loop_max_frame).count()
            return_obj.append(round_result)

        return HttpResponse(json.dumps(return_obj))


def get_progress_data(request):
    if request.method == 'GET':
        file_name = request.GET.get('video_name')
        try:
            progress_object = ProgressModel.objects.get(pk=file_name)
            return_obj = {
                'progress': progress_object.progress,
                'max_frame': progress_object.max_frame,
            }
        except ProgressModel.DoesNotExist:
            return_obj = {
                'progress': 0,
                'max_frame': 0,
            }
        return HttpResponse(json.dumps(return_obj))


def send_mail(dest, file_name):
    key = 'key-c4b7a856e0a88accf4d3fcf4f7187097'
    sandbox = 'sandbox3e44ff53154a450faa54ffdf485d7bc4.mailgun.org'
    recipient = dest

    small_count = CarsModel.objects.filter(car_type='2', file_name=file_name).count()
    medium_count = CarsModel.objects.filter(car_type='1', file_name=file_name).count()
    large_count = CarsModel.objects.filter(car_type='0', file_name=file_name).count()

    send_text = 'Total cars: ' + str(small_count+medium_count+large_count) + '\nTotal'\
                ' Trucks: ' + str(large_count) + '\nTotal '\
                'Passenger cars: ' + str(medium_count) + '\nTotal '\
                'Bikes: ' + str(small_count)

    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(sandbox)
    request = requests.post(request_url, auth=('api', key), data={
        'from': 'result@AVCS.com',
        'to': recipient,
        'subject': 'Predicted result',
        'text': send_text
        },
        files=[('attachment', open(settings.MEDIA_ROOT+'result_data/'+file_name[:file_name.find('.avi')] + '.csv')), ],)

    print 'Status: {0}'.format(request.status_code)
    print 'Body:   {0}'.format(request.text)


def resend_data(request):
    if request.method == 'GET':
        return render(request, 'main_app/resend.html')


def search_res(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        file_name = request.GET.get('file')
        result_list = ResultModel.objects.filter(file_name=file_name, email=email)
        html = ''
        for result_object in result_list:
            time_data = format(result_object.time + timedelta(hours=7), '%d/%m/%Y-%H:%M:%S')
            html += '<a href="/main/send_result?res='+result_object.unique_name+'&email='+result_object.email+'">'
            html += result_object.file_name+'</a> '+time_data+'<br>'

        return HttpResponse(html)


def send_result(request):
    if request.method == 'GET':
        unique_name = request.GET.get('res')
        email = request.GET.get('email')
        file_name = unique_name[:unique_name.find('.csv')] + '.avi'
        send_mail(email, file_name)
        return HttpResponse('success')


def login_view(request):
    return render(request, 'main_app/login.html')


def auth_and_login(request, onsuccess='/main/train_page/', onfail='/main/login/'):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        return redirect(onsuccess)
    else:
        return redirect(onfail)


@login_required(login_url='/main/login/')
def change_password_view(request):
    return render(request, 'main_app/change_password.html')


def change_password(request, onsuccess='/main/login/', onfail='/main/chgpwd/'):
    user = authenticate(username='admin', password=request.POST['password'])
    if user is not None:
        user.set_password(request.POST['new_password'])
        user.save()
        return redirect(onsuccess)
    else:
        return redirect(onfail)


def logout_session(request):
    logout(request)
    return redirect('/main/login/')


def result_image(request):
    if request.method == 'GET':
        video_name = request.GET.get('video_name')
        suffix_name = '-'+video_name[:video_name.find('.avi')] + '.png'
        html = '<div class="col-md-4">'
        list_cars = glob.glob(settings.STATICFILES_DIRS[0]+'main_app/media/result_image/*0'+suffix_name)
        for car in list_cars:
            car_string = str(car)
            car_src = car_string[car_string.find('/static'):]
            html += '<img src="'+car_src+'"><br>'
        html += '</div><div class="col-md-4">'
        list_cars = glob.glob(settings.STATICFILES_DIRS[0]+'main_app/media/result_image/*1'+suffix_name)
        for car in list_cars:
            car_string = str(car)
            car_src = car_string[car_string.find('/static'):]
            html += '<img src="'+car_src+'"><br>'
        html += '</div><div class="col-md-4">'
        list_cars = glob.glob(settings.STATICFILES_DIRS[0]+'main_app/media/result_image/*2'+suffix_name)
        for car in list_cars:
            car_string = str(car)
            car_src = car_string[car_string.find('/static'):]
            html += '<img src="'+car_src+'"><br>'
        html += '</div>'
        return HttpResponse(html)
