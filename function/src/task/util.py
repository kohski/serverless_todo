import json


class UserNotFoundError(Exception):
    pass


def fetch_user_id_from_event(event):
    if 'requestContext' in event and 'authorizer' in event['requestContext'] and 'claims' in event['requestContext']['authorizer'] and 'cognito:username' in event['requestContext']['authorizer']['claims']:
        return event['requestContext']['authorizer']['claims']['cognito:username']
    else:
        raise UserNotFoundError


def convert_return_object(ststus: int = 200, body: str = None, is_base64_encoded: bool = False):
    return {
        'statusCode': 201,
        'body': json.dumps(body) if body is not None else '',
        'isBase64Encoded': False
    }
