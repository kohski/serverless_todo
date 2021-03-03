from task import Task
from util import fetch_user_id_from_event, convert_return_object, UserNotFoundError
from jsonschema import validate, ValidationError
import json
import logging
import os


def convert_payload(event, user_id):
    payload = {}
    payload = json.loads(event['body'])
    with open(os.path.dirname(__file__) + '/create.json') as f:
        schema = json.load(f)
        validate(payload, schema)
    payload['id'] = None
    payload['meta'] = 'latest'
    payload['owner'] = user_id
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
        payload = convert_payload(event, user_id)
        task = Task(**payload)
        response = task.save()
        return convert_return_object(201, response)
    except ValidationError as e:
        logging.error(e)
        return convert_return_object(400, 'invalid parameter')
    except Exception as e:
        logging.error(e)
        return convert_return_object(400, 'unexpected error')
    except UserNotFoundError as e:
        logging.error(e)
        return convert_return_object(401, 'invalid token')
