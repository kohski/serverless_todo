from task import Task, TaskNotFoundError
from jsonschema import validate, ValidationError
import json
import logging
import os
from util import fetch_user_id_from_event, convert_return_object, InvalidTaskIdError, fetch_task_id, UserNotFoundError


def convert_savable(task, payload):
    temp_task = task.to_savable_object()
    for key in payload:
        temp_task[key] = payload[key]
    try:
        converted_task = Task(**temp_task)
        return converted_task
    except Exception as e:
        logging.error(e)
        raise Exception


def convert_payload(event):
    payload = json.loads(event['body'])
    with open(os.path.dirname(__file__) + '/update.json') as f:
        schema = json.load(f)
        validate(payload, schema)
    if type(payload['is_done']) == str:
        if payload['is_done'] == 'true':
            payload['is_done'] = True
        else:
            payload['is_done'] = False
    return payload


def lambda_handler(event, context):
    logging.info(event)
    user_id = fetch_user_id_from_event(event)

    try:
        payload = convert_payload(event)
        task_id = fetch_task_id(event)
        task = Task.get(user_id, task_id)
        converted_task = convert_savable(task, payload)
        response = converted_task.save(user_id)
        return convert_return_object(201, response)
    except UserNotFoundError as e:
        logging.error(e)
        return convert_return_object(400, 'user not found error')
    except InvalidTaskIdError as e:
        logging.error(e)
        return convert_return_object(400, 'invalid request')
    except ValidationError as e:
        logging.error(e)
        return convert_return_object(400, 'invalid parameter')
    except TaskNotFoundError as e:
        logging.error(e)
        return convert_return_object(404, 'task is not found')
    except Exception as e:
        logging.error(e)
        return convert_return_object(400, 'unexpected error')
