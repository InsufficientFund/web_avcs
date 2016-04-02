from main_app.models import CarsModel
from main_app.models import ProgressModel

def save_type(file_name, car_type):
    db = CarsModel(car_type=car_type, file_name=file_name)
    db.save()


def update_progress(file_name, progress, max_frame):
    db = ProgressModel(file_name=file_name, progress=progress, max_frame=max_frame)
    db.save()

