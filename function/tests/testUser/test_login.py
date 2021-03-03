import pytest
from login import lambda_handler
import json


@pytest.fixture(params=[
    {
        'description': 'valid case',
        'body': {
            'username': 'existing_user_id',
            'password': 'Test1234#'
        }
    },
    {
        'description': 'invalid username',
        'body': {
            'username': 'not_existing_user_id',
            'password': 'Test1234#'
        }
    },
    {
        'description': 'invalid password',
        'body': {
            'username': 'existing_user_id',
            'password': 'not_valid_password'
        }
    }
])
def request_params(request):
    return request.param


@pytest.fixture
def event(request_params):
    return {
        "resource": "/task/{task_id}",
        "path": "/auth/login",
        "httpMethod": "GET",
        "headers": {},
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "stageVariables": None,
        "body": json.dumps(request_params['body']),
        "isBase64Encoded": False
    }


def test_valid_login(event, context, request_params, idp_create_init_data):
    if request_params['description'] != 'valid case':
        pytest.skip('not target case')
    response = lambda_handler(event, context)
    body = json.loads(response['body'])
    assert response['statusCode'] == 200
    assert'AccessToken' in body
    assert'IdToken' in body
    assert'RefreshToken' in body


def test_raise_invalid_username(event, context, request_params, idp_create_init_data):
    if request_params['description'] != 'invalid username':
        pytest.skip('not target case')
    response = lambda_handler(event, context)
    assert response == {
        'statusCode': 401,
        'body': 'user not found error',
        'isBase64Encoded': False
    }


def test_raise_invalid_password(event, context, request_params, idp_create_init_data):
    if request_params['description'] != 'invalid password':
        pytest.skip('not target case')
    response = lambda_handler(event, context)
    assert response == {
        'statusCode': 401,
        'body': 'not authorized error',
        'isBase64Encoded': False
    }
