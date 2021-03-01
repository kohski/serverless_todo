import json
from jsonschema import validate, ValidationError
import os
import logging


class User:

    def __init__(
        self,
        id: str,
        email: str,
        given_name: str,
        family_name: str,
        needs_validation: bool = True
    ):
        self.id = id
        self.email = email
        self.given_name = given_name
        self.family_name = family_name

        if needs_validation:
            with open(os.path.dirname(__file__) + '/user.json') as f:
                schema = json.loads(f.read())
                try:
                    validate(vars(self), schema)
                except ValidationError as e:
                    logging.error(e)
                    raise e
