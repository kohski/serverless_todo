import logging
import json
from task import Task, TaskNotFoundError, NotTaskOwnerError


class UserNotFoundError(Exception):
    pass


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

    task_id = ''
    if 'pathParameters' in event and 'task_id' in event['pathParameters']:
        task_id = event['pathParameters']['task_id']
    else:
        return {
            'statusCode': 400,
            'body': 'invalid request',
            'isBase64Encoded': False
        }

    try:
        raw_task = Task.get(user_id, task_id)
        response = raw_task.delete(user_id)
        return {
            'statusCode': 200,
            'body': json.dumps(response),
            'isBase64Encoded': False
        }
    except TaskNotFoundError as e:
        logging.error(e)
        return {
            'statusCode': 404,
            'body': 'task is not found',
            'isBase64Encoded': False
        }
    except NotTaskOwnerError as e:
        logging.error(e)
        return {
            'statusCode': 403,
            'body': 'not task owner',
            'isBase64Encoded': False
        }
    except Exception as e:
        logging.error(e)
        return {
            'statusCode': 400,
            'body': 'unexpected error',
            'isBase64Encoded': False
        }
