from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from django.conf import settings
from django.core import serializers
import cv2
import base64
import json
import time
from AVCS import AVCS
from lbp_feature import lbp_feature
from neural_net import neural_net
from models import CarsModel
from models import ProgressModel
import glob
import re
import csv
import os
import uuid
import requests
from multiprocessing import Pool



def index(request):
    form = UploadFileForm()
    return render(request, 'main_app/index.html', {'form': form})


def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = handle_uploaded_file(request.FILES['file'])
            return HttpResponse(filename)
        else:
            return HttpResponse("Invalid")
    else:
        form = UploadFileForm()
        return HttpResponse("failed")
    # return render(request, 'upload.html', {'form': form})


    # return HttpResponse("Hello, world. You're at the polls index.")
# Create your views here.

def handle_uploaded_file(f):
    ext = f.name.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    with open(settings.MEDIA_ROOT+"upload/"+filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return filename


def train_page(request):
    if request.method == 'GET':
        return render(request, 'main_app/train_page.html')


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]


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


def detect(request):
    if request.is_ajax():
        if request.method == 'POST':
            #print 'Raw Data: "%s"' % request.body
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
                        car_name +'"> <img src="' + \
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
            neural_network = neural_net(75, 3)
            neural_network.create_struct(150)
            # file_train = '/home/sayong/Project/AVCS/Car-counter-using-python-opencv/list_data_raw.csv'
            # file_test = '/home/sayong/Project/AVCS/Car-counter-using-python-opencv/list_test_raw.csv'
            file_train = settings.STATICFILES_DIRS[0]+'main_app/media/train_data.csv'
            #neural_network.data_input(feature_list, answer, "train")
            neural_network.file_input(file_train)
            #neural_network.file_input(file_test, type_set='test')
            #test_data, test_answer = neural_network.get_test_data()
            neural_network.training(5000)
            neural_network.save_model(settings.STATICFILES_DIRS[0])
            #print neural_network.predict(test_data[0])
            #print test_answer[0]
            return HttpResponse('OK')


def predict_page(request):
    if request.method == 'GET':
        form = UploadFileForm()
        return render(request, 'main_app/predict_page.html',  {'form': form})


def get_sample_frame(request):
    if request.is_ajax():
        if request.method == 'GET':
            filename = request.GET['video_name']
            counter = AVCS()
            counter.readVideo(settings.MEDIA_ROOT+"upload/"+filename, filename)
            #import ipdb; ipdb.set_trace()
            frame = counter.sampleImage()
            frame_name = filename[:filename.find('.avi')] + '.png'
            write_path = settings.STATICFILES_DIRS[0]+'main_app/media/sample_image/'+frame_name
            print write_path
            cv2.imwrite(write_path, frame)
            return HttpResponse('sample_image/'+frame_name)



def predict(request):
    if request.is_ajax():
        if request.method == 'POST':
            #print 'Raw Data: "%s"' % request.body
            json_data = json.loads(request.body)
            print json_data
            #counter = AVCS()
            video_path = settings.MEDIA_ROOT+'upload/' + json_data['video_name']
            print video_path
            #counter.readVideo(video_path, json_data['video_name'])
            # counter.addLane((131, 142), (203, 142), (123, 245), (213, 245))
            # counter.addLane((205, 142), (275, 142), (215, 245), (316, 245))
            # counter.addLane((155, 182), (225, 182), (123, 285), (232, 285))
            # counter.addLane((227, 182), (302, 182), (234, 285), (356, 285))
            lane_data = json.loads(json_data['data'])
            # for lane in lane_data:
            #     up_left = tuple(map(int,lane["up_left"]))
            #     up_right = tuple(map(int,lane["up_right"]))
            #     low_left = tuple(map(int,lane["low_left"]))
            #     low_right = tuple(map(int,lane["low_right"]))
            #     counter.addLane(up_left, up_right, low_left, low_right)
            # start_time = time.time()
            # counter.run(mode='predict', cntStatus=False, showVid=False)
            # elapsed_time = time.time() - start_time
            #print elapsed_time
            pool = Pool(processes=1)
            result = pool.apply_async(asnyc_count, [json_data['email'], json_data['video_name'], lane_data])

            return HttpResponse('OK_OK')


def asnyc_count(dest, file_name, lane_data):
    counter = AVCS()
    video_path = settings.MEDIA_ROOT+'upload/' + file_name
    counter.readVideo(video_path, file_name)
    for lane in lane_data:
        up_left = tuple(map(int,lane["up_left"]))
        up_right = tuple(map(int,lane["up_right"]))
        low_left = tuple(map(int,lane["low_left"]))
        low_right = tuple(map(int,lane["low_right"]))
        counter.addLane(up_left, up_right, low_left, low_right)
    counter.run(mode='predict', cntStatus=False, showVid=False)
    send_mail(dest, file_name)


def get_detect_status(request):
    if request.method == 'GET':
        all_obj = CarsModel.objects.all()
        # return_str = [str(obj) for obj in all_obj.values()]
        return_str = serializers.serialize("json", CarsModel.objects.all())
        return HttpResponse(return_str)


def get_graph_data(request):
    if request.method == 'GET':
        # all_obj = CarsModel.objects.all()
        file_name = request.GET.get('video_name')
        # import ipdb; ipdb.set_trace()
        # return_str = [str(obj) for obj in all_obj.values()]
        small_type_count = CarsModel.objects.filter(car_type='2',file_name=file_name).count()
        medium_type_count = CarsModel.objects.filter(car_type='1',file_name=file_name).count()
        large_type_count = CarsModel.objects.filter(car_type='0',file_name=file_name).count()
        # return_str = serializers.serialize("json", all_obj)
        return_obj = {
            's': small_type_count,
            'm': medium_type_count,
            'l': large_type_count,
        }

        return HttpResponse(json.dumps(return_obj))
        # return HttpResponse(return_str)

def get_progress_data(request):
    if request.method == 'GET':
        # all_obj = CarsModel.objects.all()
        file_name = request.GET.get('video_name')
        # import ipdb; ipdb.set_trace()
        # return_str = [str(obj) for obj in all_obj.values()]
        # small_type_count = CarsModel.objects.filter(car_type='2',file_name=file_name).count()
        # medium_type_count = CarsModel.objects.filter(car_type='1',file_name=file_name).count()
        # large_type_count = CarsModel.objects.filter(car_type='0',file_name=file_name).count()
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
        # return_str = serializers.serialize("json", all_obj)
        # return_obj = {
        #     's': small_type_count,
        #     'm': medium_type_count,
        #     'l': large_type_count,
        # }

        return HttpResponse(json.dumps(return_obj))
        # return HttpResponse(return_str)

def send_mail(dest, file_name):
    key = 'key-c4b7a856e0a88accf4d3fcf4f7187097'
    sandbox = 'sandbox3e44ff53154a450faa54ffdf485d7bc4.mailgun.org'
    recipient = dest

    small_count = CarsModel.objects.filter(car_type='2',file_name=file_name).count()
    medium_count = CarsModel.objects.filter(car_type='1',file_name=file_name).count()
    large_count = CarsModel.objects.filter(car_type='0',file_name=file_name).count()

    send_text = 'Total cars: ' + str(small_count+medium_count+large_count)+ '\nTotal'\
                ' Trucks: ' + str(large_count)+ '\nTotal '\
                'Passenger cars: ' + str(medium_count)+ '\nTotal '\
                'Bikes: ' + str(small_count)

    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(sandbox)
    request = requests.post(request_url, auth=('api', key), data={
        'from': 'result@AVCS.com',
        'to': recipient,
        'subject': 'Predicted result',
        'text': send_text
    })

    print 'Status: {0}'.format(request.status_code)
    print 'Body:   {0}'.format(request.text)
