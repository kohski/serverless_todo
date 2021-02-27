import json
from jsonschema import validate, ValidationError
import os
import logging
import boto3

logging.basicConfig(level=logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


class TaskNotFoundError(Exception):
    pass


class Task:

    def __init__(
        self,
        id: str,
        title: str,
        created_at: str,
        updated_at: str,
        meta: str = 'latest',
        priority: str = 'medium',
        is_done: str = False,
        content: str = None,
        needs_validation: bool = True
    ):
        self.id = id
        self.meta = meta
        self.title = title
        self.content = content
        self.is_done = is_done
        self.priority = priority
        self.created_at = created_at
        self.updated_at = updated_at
        for_search = ''
        for_search += title if title is not None else ''
        for_search += content if content is not None else ''
        self.for_search = for_search

        try:
            if needs_validation:
                with open(os.path.dirname(__file__) + '/task.json') as f:
                    schema = json.load(f)
                    validate(vars(self), schema)
        except ValidationError as e:
            logging.error(e)
            raise e
        except Exception as e:
            logging.error(e)
            raise e

    def save():
        pass

    @classmethod
    def get(cls, user_id, task_id):
        item = table.get_item(
            Key={
                'id': "Task:{}:{}".format(user_id, task_id),
                'meta': 'latest'
            }
        )
        if 'Item' in item:
            return item['Item']
        else:
            raise TaskNotFoundError

    def update():
        pass

    def to_object(self):
        return vars(self)

    @classmethod
    def search():
        pass