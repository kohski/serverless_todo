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

@pytest.mark.parametrize("word,is_done,priority", [
    (word, is_done, priority)
    for word in ['A', '内容', '']
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
            "title": "タイトル",
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
def test_raise_invalid_case(request, invalid_event, context, ulid_mock):
    event = {
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
            "title": "タイトル" if request.get('title') is None else request.get('title'),
            "priority": "medium" if request.get('priority') is None else request.get('priority'),
            "is_done": 'false' if request.get('is_done') is None else request.get('is_done'),
            "content": "内容" if request.get('content') is None else request.get('content')
        }),
        "isBase64Encoded": False
    }
    response = lambda_handler(event, context)
    assert response == {
        'statusCode': 400,
        'body': 'invalid parameter',
        'isBase64Encoded': False
    }
