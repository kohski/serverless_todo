import pytest
from datetime import datetime
from create import lambda_handler
import boto3
import os
import json


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


# ------------------------------------------
#               valid pattern
# ------------------------------------------
VALID_PRIORITY_LIST = [
    "high",
    "medium",
    "low"
]

VALID_IS_DONE_LIST = [
    True,
    False
]

VALID_CONTENT_LIST = [
    None,
    "",
    "タスク内容A"
]


@pytest.fixture(params=VALID_PRIORITY_LIST)
def valid_priority_params(request):
    return request.param


@pytest.fixture(params=VALID_IS_DONE_LIST)
def valid_is_done_params(request):
    return request.param


@pytest.fixture(params=VALID_CONTENT_LIST)
def valid_content_params(request):
    return request.param


@pytest.fixture
def valid_task(valid_priority_params, valid_is_done_params, valid_content_params):
    return {
        "description": "valid case",
        'payload': {
            "id": "ABCDEFGHIJKLMNOPQRSTUVW000",
            "title": "タイトル",
            "owner": "latest",
            "priority": valid_priority_params,
            "is_done": valid_is_done_params,
            "content": valid_content_params
        }
    }


@pytest.fixture()
def valid_event(valid_task):
    return {
        "resource": "/task/",
        "path": "/task",
        "httpMethod": 'POST',
        "headers": {},
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": {},
        "stageVariables": None,
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": "68f2ed3a-3726-439d-81cb-171dab716733",
                    "aud": "19gqr90c608tn8gp7j9nvop7h7",
                    "event_id": "55536ceb-c042-4c18-8a25-8bd4e4c2b28d",
                    "token_use": "id",
                    "auth_time": str(int(datetime.now().timestamp())),
                    "iss": "https://cognito-idp.ap-northeast-1.amazonaws.com/ap-northeast-*",
                    "cognito:username": "existing_user_id",
                    "exp": "Sun Feb 28 01:38:19 UTC 2021",
                    "iat": "Sun Feb 28 00:38:20 UTC 2021",
                    "email": "test@gmail.com"
                }
            },
            "resourcePath": "/task",
            "httpMethod": "GET",
            "path": "/prod/task/123456",
            "requestTimeEpoch": int(datetime.now().timestamp()),
            "identity": {}
        },
        "body": valid_task['payload'],
        "isBase64Encoded": False
    }


def test_existing_task_and_requested_by_task_owner(valid_event, context, ulid_mock):
    response = lambda_handler(valid_event, context)
    del response['body']
    assert response == {
        'statusCode': 201,
        'isBase64Encoded': False
    }
    item = table.get_item(
        Key={
            'id': 'Task:ABCDEFGHIJKLMNOPQRSTUVW999',
            'meta': 'latest'
        }
    )
    assert 'Item' in item


# ------------------------------------------
#               invalid pattern
# ------------------------------------------


INVALID_PAYLOAD_LIST = [
    {
        "title": ""
    },
    {
        "title": None
    },
    {
        "title": "a" * 101
    },
    {
        "content": "a" * 2001
    },
    {
        "priority": "invalid_priority_value"
    },
    {
        "is_done": "invalid_is_done_value"
    },
]


@pytest.fixture(params=INVALID_PAYLOAD_LIST)
def invalid_payload(request):
    return request.param


@pytest.fixture
def invalid_task(invalid_payload):
    return {
        "description": "invalid case",
        'payload': {
            "title": invalid_payload.get('title'),
            "priority": "medium" if invalid_payload.get('priority') is None else invalid_payload.get('priority'),
            "is_done": True if invalid_payload.get('is_done') is None else invalid_payload.get('is_done'),
            "content": "内容" if invalid_payload.get('content') is None else invalid_payload.get('content')
        }
    }


@pytest.fixture()
def invalid_event(invalid_task):
    return {
        "resource": "/task/",
        "path": "/task",
        "httpMethod": 'POST',
        "headers": {},
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": {},
        "stageVariables": None,
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": "68f2ed3a-3726-439d-81cb-171dab716733",
                    "aud": "19gqr90c608tn8gp7j9nvop7h7",
                    "event_id": "55536ceb-c042-4c18-8a25-8bd4e4c2b28d",
                    "token_use": "id",
                    "auth_time": str(int(datetime.now().timestamp())),
                    "iss": "https://cognito-idp.ap-northeast-1.amazonaws.com/ap-northeast-*",
                    "cognito:username": "existing_user_id",
                    "exp": "Sun Feb 28 01:38:19 UTC 2021",
                    "iat": "Sun Feb 28 00:38:20 UTC 2021",
                    "email": "test@gmail.com"
                }
            },
            "resourcePath": "/task",
            "httpMethod": "GET",
            "path": "/prod/task/123456",
            "requestTimeEpoch": int(datetime.now().timestamp()),
            "identity": {}
        },
        "body": invalid_task['payload'],
        "isBase64Encoded": False
    }


def test_raise_invalid_case(invalid_event, context, ulid_mock):
    response = lambda_handler(invalid_event, context)
    assert response == {
        'statusCode': 400,
        'body': 'invalid parameter',
        'isBase64Encoded': False
    }
