import logging
from task import Task, TaskNotFoundError, NotTaskOwnerError
from util import fetch_user_id_from_event, convert_return_object, InvalidTaskIdError, fetch_task_id, UserNotFoundError


def lambda_handler(event, context):
    logging.info(event)
    user_id = fetch_user_id_from_event(event)
    task_id = fetch_task_id(event)

    try:
        raw_task = Task.get(user_id, task_id)
        response = raw_task.delete(user_id)
        return convert_return_object(200, response)
    except UserNotFoundError as e:
        logging.error(e)
        return convert_return_object(400, 'user not found error')
    except InvalidTaskIdError as e:
        logging.error(e)
        return convert_return_object(400, 'invalid request')
    except TaskNotFoundError as e:
        logging.error(e)
        return convert_return_object(404, 'task is not found')
    except NotTaskOwnerError as e:
        logging.error(e)
        return convert_return_object(403, 'not task owner')
    except Exception as e:
        logging.error(e)
        return convert_return_object(400, 'unexpected error')
