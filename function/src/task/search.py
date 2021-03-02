import logging
from task import Task, TaskNotFoundError, NotTaskOwnerError
from util import fetch_user_id_from_event, convert_return_object, UserNotFoundError


def fetch_search_info(event):
    search_info = {}
    if 'queryStringParameters' in event and event['queryStringParameters'] is not None:
        search_info = event['queryStringParameters']
    return search_info


def lambda_handler(event, context):
    logging.info(event)
    user_id = fetch_user_id_from_event(event)
    search_info = fetch_search_info(event)

    try:
        tasks = Task.search(user_id, **search_info)
        return convert_return_object(200, tasks)
    except TaskNotFoundError as e:
        logging.error(e)
        return convert_return_object(404, 'task is not found')
    except UserNotFoundError as e:
        logging.error(e)
        return convert_return_object(400, 'user not found error')
    except NotTaskOwnerError as e:
        logging.error(e)
        return convert_return_object(403, 'not task owner')
    except Exception as e:
        logging.error(e)
        return convert_return_object(400, 'unexpected error')
