from main_app.models import CarsModel


def save_type(file_name, car_type):
    db = CarsModel(car_type=car_type, file_name=file_name)
    db.save()
