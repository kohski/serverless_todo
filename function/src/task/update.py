from task import Task, TaskNotFoundError
from jsonschema import validate, ValidationError
import json
import logging
import os


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


def lambda_handler(event, context):
    logging.info(event)
    user_id = ''
    if 'requestContext' in event and 'authorizer' in event['requestContext'] and 'claims' in event['requestContext']['authorizer'] and 'cognito:username' in event['requestContext']['authorizer']['claims']:
        user_id = event['requestContext']['authorizer']['claims']['cognito:username']
    else:
        return {
            'statusCode': 401,
            'body': 'invalid token',
            'isBase64Encoded': False
        }

    payload = {}
    try:
        payload = json.loads(event['body'])
        with open(os.path.dirname(__file__) + '/update.json') as f:
            schema = json.load(f)
            validate(payload, schema)
        task_id = event['pathParameters']['task_id']
        task = Task.get(user_id, task_id)
        converted_task = convert_savable(task, payload)
        response = converted_task.save(user_id)
        return {
            'statusCode': 201,
            'body': json.dumps(response),
            'isBase64Encoded': False
        }
    except ValidationError as e:
        logging.error(e)
        return {
            'statusCode': 400,
            'body': 'invalid parameter',
            'isBase64Encoded': False
        }
    except TaskNotFoundError as e:
        logging.error(e)
        return {
            'statusCode': 404,
            'body': 'task is not found',
            'isBase64Encoded': False
        }
    except Exception as e:
        logging.error(e)
        return {
            'statusCode': 400,
            'body': 'unexpected error',
            'isBase64Encoded': False
        }
