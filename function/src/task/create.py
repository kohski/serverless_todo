from task import Task
from jsonschema import validate, ValidationError
import json
import logging
import os


def lambda_handler(event, context):
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
        if 'body' in event:
            payload = event['body']
            with open(os.path.dirname(__file__) + '/create.json') as f:
                schema = json.load(f)
                validate(payload, schema)
            payload['id'] = None
            payload['owner'] = user_id
        task = Task(**payload)
        response = task.save()
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
    except Exception as e:
        logging.error(e)
        return {
            'statusCode': 400,
            'body': 'unexpected error',
            'isBase64Encoded': False
        }
