import json
from jsonschema import validate, ValidationError
import os


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

        try:
            if needs_validation:
                with open(os.path.dirname(__file__) + '/task.json') as f:
                    schema = json.load(f)
                    validate(vars(self), schema)
        except ValidationError as e:
            raise e
        except Exception as e:
            raise e

    def save():
        pass

    def get():
        pass

    def update():
        pass

    def to_object(self):
        return vars(self)

    @classmethod
    def search():
        pass
