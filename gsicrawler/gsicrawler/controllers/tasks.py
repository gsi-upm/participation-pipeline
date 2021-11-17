import json
from celery.task.control import inspect
from flask import current_app


def get(taskId, *args, **kwargs):
    task = current_app.tasks.celery.AsyncResult(taskId)
    response = {'task_id': task.id, 'status': task.state}
    if task.ready():
        response['results'] = task.result
        return response, 200
    return response, 202
