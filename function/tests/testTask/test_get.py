import pytest
from datetime import datetime
from get import lambda_handler
import json


TEST_PARAMS = [
    {
        'description': 'existing task and requested by owner',
        'method': 'GET',
        'path': '/task/{task_id}',
        'task_id': 'ABCDEFGHIJKLMNOPQRSTUVW000',
        'username': 'existing_user_id'
    },
    {
        'description': 'existing task id and requested by not task owner',
        'method': 'GET',
        'path': '/task/{task_id}',
        'task_id': 'ABCDEFGHIJKLMNOPQRSTUVW024',
        'username': 'existing_user_id'
    },
    {
        'description': 'not existing task id',
        'method': 'GET',
        'path': '/task/{task_id}',
        'task_id': 'NOTEXISTINGTASK',
        'username': 'existing_user_id'
    }
]


@pytest.fixture(params=TEST_PARAMS, ids=list(map(lambda x: x['description'], TEST_PARAMS)))
def request_params(request):
    return request.param


@pytest.fixture()
def event(request_params):
    return {
        "resource": "/task/{task_id}",
        "path": "/task/{}".format(request_params['task_id']),
        "httpMethod": "GET",
        "headers": {},
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": {
            "task_id": request_params['task_id']
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
                    "cognito:username": request_params['username'],
                    "exp": "Sun Feb 28 01:38:19 UTC 2021",
                    "iat": "Sun Feb 28 00:38:20 UTC 2021",
                    "email": "test@gmail.com"
                }
            },
            "resourcePath": "/task/{task_id}",
            "httpMethod": "GET",
            "path": "/prod/task/123456",
            "requestTimeEpoch": int(datetime.now().timestamp()),
            "identity": {}
        },
        "body": None,
        "isBase64Encoded": False
    }


def test_existing_task_and_requested_by_task_owner(event, context, request_params):
    if request_params['description'] != 'existing task and requested by owner':
        pytest.skip('not target case')
    response = lambda_handler(event, context)
    assert response == {
        'statusCode': 200,
        'body': json.dumps({
            "id": "ABCDEFGHIJKLMNOPQRSTUVW000",
            "meta": "latest",
            "title": "件名A",
            "owner": "existing_user_id",
            "content": "内容A",
            "is_done": True,
            "priority": "high",
            "created_at": 1614342166.0,
            "updated_at": 1614342166.0
        }),
        'isBase64Encoded': False
    }


def test_existing_task_id_and_requested_by_not_task_owner(event, context, request_params):
    if request_params['description'] != 'existing task id and requested by not task owner':
        pytest.skip('not target case')
    response = lambda_handler(event, context)
    assert response == {
        'statusCode': 403,
        'body': 'not task owner',
        'isBase64Encoded': False
    }


def test_not_existing_task_id(event, context, request_params):
    if request_params['description'] != 'not existing task id':
        pytest.skip('not target case')
    response = lambda_handler(event, context)
    assert response == {
        'statusCode': 404,
        'body': 'task is not found',
        'isBase64Encoded': False
    }
