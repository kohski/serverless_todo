import json
from jsonschema import validate, ValidationError
import boto3
from botocore.exceptions import ClientError
import os
import logging
from decimal import Decimal
from datetime import datetime
import ulid

logging.basicConfig(level=logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


class TaskNotFoundError(Exception):
    pass


class NotTaskOwnerError(Exception):
    pass


class Task:

    def __init__(
        self,
        title: str,
        owner: str,
        id: str = None,
        meta: str = 'latest',
        priority: str = 'medium',
        is_done: str = False,
        content: str = None,
        created_at: int = None,
        updated_at: int = None,
        needs_validation: bool = True
    ):
        self.id = id
        self.meta = meta
        self.title = title
        self.owner = owner
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

    def save(self):
        if self.id is None:
            self.id = str(ulid.new())
            self.created_at = int(datetime.now().timestamp())
            self.updated_at = int(datetime.now().timestamp())
            item = self.to_savable_object()
            item['id'] = 'Task:{}'.format(self.id)
        else:
            pass
        try:
            table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(id)'
            )
            return self.to_returnable_object()
        except ClientError as e:
            import pdb
            pdb.set_trace()
            logging.error(e)
            raise e
        except Exception as e:
            import pdb
            pdb.set_trace()
            logging.error(e)
            raise e

    @classmethod
    def get(cls, user_id, task_id):
        try:
            item = table.get_item(
                Key={
                    'id': "Task:{}".format(task_id),
                    'meta': "latest"
                }
            )
            if 'Item' in item:
                if item['Item'].get('owner') == user_id:
                    item['Item']['id'] = task_id
                    task = cls(**item['Item'])
                    return task
                else:
                    raise NotTaskOwnerError
            else:
                raise TaskNotFoundError
        except TaskNotFoundError as e:
            logging.error(e)
            raise e
        except ClientError as e:
            logging.error(e)
            raise e
        except Exception as e:
            raise e

    def to_returnable_object(self):
        if hasattr(self, 'created_at'):
            self.created_at = float(self.created_at)
        if hasattr(self, 'updated_at'):
            self.updated_at = float(self.updated_at)
        if hasattr(self, 'for_search'):
            del self.for_search
        return vars(self)

    def to_savable_object(self):
        if hasattr(self, 'created_at') and self.created_at is not None:
            self.created_at = Decimal(str(self.created_at))
        if hasattr(self, 'updated_at') and self.updated_at is not None:
            self.updated_at = Decimal(str(self.updated_at))
        if hasattr(self, 'content') and self.content == '':
            self.content = None
        return vars(self)

    @classmethod
    def search():
        pass
