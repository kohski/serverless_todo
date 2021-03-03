import json
from jsonschema import validate, ValidationError
from botocore.exceptions import ClientError
import os
import logging
import boto3


idp = boto3.client('cognito-idp')


class UserNotFoundError(Exception):
    pass


class NotAuthorizedError(Exception):
    pass


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

    @classmethod
    def login(cls, username, password):
        try:
            res = idp.admin_initiate_auth(
                UserPoolId=os.environ['USER_POOL_ID'],
                ClientId=os.environ['CLIENT_ID'],
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            return res
        except ClientError as e:
            logging.error(e)
            if e.response['Error']['Code'] == 'UserNotFoundException':
                raise UserNotFoundError
            if e.response['Error']['Code'] == 'NotAuthorizedException':
                raise NotAuthorizedError
