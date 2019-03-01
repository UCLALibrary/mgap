from .celery import app

@app.task
def noop(x):
    return x
