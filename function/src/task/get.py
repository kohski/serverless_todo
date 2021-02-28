import logging
import json
from task import Task


class UserNotFoundError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


def lambda_handler(event, context):
    logging.info(event)
    user_id = ''
    if 'requestContext' in event and 'authorizer' in event['requestContext'] and 'claims' in event['requestContext']['authorizer'] and 'cognito:username' in event['requestContext']['authorizer']['claims']:
        user_id = event['requestContext']['authorizer']['claims']['cognito:username']
    else:
        return {
            'statusCode': 401,
            'isBase64Encoded': False
        }

    task_id = ''
    if 'pathParameters' in event and 'task_id' in event['pathParameters']:
        task_id = event['pathParameters']['task_id']
    else:
        return {
            'statusCode': 400,
            'isBase64Encoded': False
        }

    raw_task = Task.get(user_id, task_id)
    task = raw_task.to_returnable_object()
    return {
        'statusCode': 200,
        'body': json.dumps(task),
        'isBase64Encoded': False
    }
