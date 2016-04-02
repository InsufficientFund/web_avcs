from main_app.models import CarsModel
from main_app.models import ProgressModel
from main_app.models import ResultModel


def save_type(file_name, car_type,frame):
    db = CarsModel(car_type=car_type, file_name=file_name, frame=frame)
    db.save()


def update_progress(file_name, progress, max_frame):
    db = ProgressModel(file_name=file_name, progress=progress, max_frame=max_frame)
    db.save()


def save_result(unique_name, file_name, email):
    db = ResultModel(unique_name=unique_name, file_name=file_name, email=email)
    db.save()
