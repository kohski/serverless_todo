import json


class UserNotFoundError(Exception):
    pass


class InvalidTaskIdError(Exception):
    pass


def fetch_user_id_from_event(event):
    if 'requestContext' in event and 'authorizer' in event['requestContext'] and 'claims' in event['requestContext']['authorizer'] and 'cognito:username' in event['requestContext']['authorizer']['claims']:
        return event['requestContext']['authorizer']['claims']['cognito:username']
    else:
        raise UserNotFoundError


def convert_return_object(ststus: int = 200, body: str = None, is_base64_encoded: bool = False):
    return_body = ''
    if type(body) == dict:
        return_body = json.dumps(body)
    elif type(body) == str:
        return_body = body
    else:
        return_body = ''
    return {
        'statusCode': ststus,
        'body': return_body,
        'isBase64Encoded': False
    }
