import logging
import json
from task import Task


class UserNotFoundError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


def lambda_handler(event, context):
    user_id = ''
    if 'requestContext' in event and 'authorizer' in event['requestContext'] and 'jwt' in event['requestContext']['authorizer'] and 'claims' in event['requestContext']['authorizer']['jwt'] and 'cognito:username' in event['requestContext']['authorizer']['jwt']['claims']:
        user_id = event['requestContext']['authorizer']['jwt']['claims']['cognito:username']
    else:
        raise UserNotFoundError

    task_id = ''
    if 'pathParameters' in event and 'task_id' in event['pathParameters']:
        task_id = event['pathParameters']['task_id']
    else:
        raise TaskNotFoundError

    raw_task = Task.get(user_id, task_id)
    task = raw_task.to_returnable_object()
    return {
        'statusCode': 200,
        'body': json.dumps(task),
        'isBase64Encoded': False
    }
