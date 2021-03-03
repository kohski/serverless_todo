import pytest
from datetime import datetime
from update import lambda_handler
import boto3
import os
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


# ------------------------------------------
#               valid pattern
# ------------------------------------------

@pytest.mark.parametrize("word,is_done,priority", [
    (word, is_done, priority)
    for word in [None, "", "修正後内容"]
    for is_done in ['true', 'false', True, False]
    for priority in ['high', 'medium', 'low']
])
def test_existing_task_and_requested_by_task_owner(word, is_done, priority, context, ulid_mock):
    event = {
        "resource": "/task/",
        "path": "/task",
        "httpMethod": 'POST',
        "headers": {},
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": {
            "task_id": "ABCDEFGHIJKLMNOPQRSTUVW000"
        },
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
        "body": json.dumps({
            "title": "修正後タイトル",
            "priority": priority,
            "is_done": is_done,
            "content": word
        }),
        "isBase64Encoded": False
    }
    response = lambda_handler(event, context)
    del response['body']
    assert response == {
        'statusCode': 201,
        'isBase64Encoded': False
    }
    item = table.get_item(
        Key={
            'id': 'Task:ABCDEFGHIJKLMNOPQRSTUVW000',
            'meta': 'latest'
        }
    )
    assert item['Item']['title'] == '修正後タイトル'


# ------------------------------------------
#               not found pattern
# ------------------------------------------

@pytest.fixture()
def not_found_event():
    return {
        "resource": "/task/",
        "path": "/task",
        "httpMethod": 'POST',
        "headers": {},
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": {
            'task_id': 'NOTEXISTINGTASK'
        },
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
        "body": json.dumps({
            "title": "タイトル",
            "priority": "medium",
            "is_done": 'true',
            "content": "内容"
        }),
        "isBase64Encoded": False
    }


def test_raise_not_found_case(not_found_event, context):
    response = lambda_handler(not_found_event, context)
    assert response == {
        'statusCode': 404,
        'body': 'task is not found',
        'isBase64Encoded': False
    }
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
def invalid_event(request):
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
        "body": json.dumps({
            "title": request.param.get('title'),
            "priority": "medium" if request.param.get('priority') is None else request.param.get('priority'),
            "is_done": 'true' if request.param.get('is_done') is None else request.param.get('is_done'),
            "content": "内容" if request.param.get('content') is None else request.param.get('content')
        }),
        "isBase64Encoded": False
    }


def test_raise_invalid_case(invalid_event, context, ulid_mock):
    response = lambda_handler(invalid_event, context)
    assert response == {
        'statusCode': 400,
        'body': 'invalid parameter',
        'isBase64Encoded': False
    }
