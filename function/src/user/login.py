import logging
from user import UserNotFoundError, NotAuthorizedError, User
import json


def fetch_params(event):
    return json.loads(event['body'])


def convert_return_object(ststus: int = 200, body: str = None, is_base64_encoded: bool = False):
    return_body = ''
    if type(body) == dict or type(body) == list:
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


def lambda_handler(event, context):
    logging.info(event)
    query_string = fetch_params(event)
    try:
        response = User.login(**query_string)
        return convert_return_object(200, response.get('AuthenticationResult'))
    except UserNotFoundError as e:
        logging.error(e)
        return convert_return_object(401, 'user not found error')
    except NotAuthorizedError as e:
        logging.error(e)
        return convert_return_object(401, 'not authorized error')
