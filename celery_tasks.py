from celery import Celery
import filters

conf = dict(
    task_serializer='pickle',
    result_serializer='pickle',
    accept_content=['pickle'],
)
app = Celery(
    broker='redis://localhost',
    backend='redis://localhost',
)
app.config_from_object(conf)


@app.task
def ascii_filter(frame):
    return filters.ascii(frame)
