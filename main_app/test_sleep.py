import time
import random
from main_app.models import avcs_model
def run_sleep():
    for i in range(1,10):
        a = avcs_model(data1=str(random.randint(1,10)))
        a.save()
