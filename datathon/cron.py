from .models import Dataset

def my_cron_job():
    Dataset.objects.create(name="haha")