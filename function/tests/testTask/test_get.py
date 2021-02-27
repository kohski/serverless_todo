import pytest
from datetime import datetime
from get import lambda_handler
import uuid
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
        'path': '/task/{task_id}',  # 024 ~ はother_user_id所属のタスク
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


@ pytest.fixture()
def context():
    # id = str(uuid.uuid4())
    stream = str(uuid.uuid4()).replace("-", "")
    func_name = "test_function"
    account = "999999999999"
    yyyymmdd = datetime.now().strftime("%Y/%m/%d")

    class context():
        def __init__(self):
            self.aws_request_id = str(uuid.uuid4())
            self.log_group_name = '/aws/lambda/' + func_name
            self.log_stream_name = yyyymmdd + '/[$LATEST]' + stream
            self.function_name = 'print_context'
            self.memory_limit_in_mb = '128'
            self.function_version = '$LATEST'
            self.invoked_function_arn = 'arn:aws:lambda:ap-northeast-1:' + \
                account + ':function:' + func_name
            self.client_context = None
            self.identity = '999'
    return context()


@pytest.fixture()
def event(request_params):
    return {
        "version": "2.0",
        "routeKey": "GET /test",
        "rawPath": "/test",
        "rawQueryString": "",
        "headers": {},
        "pathParameters": {
            "task_id": request_params['task_id']
        },
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {
                        "auth_time": str(int(datetime.now().timestamp())),
                        "cognito:username": request_params['username'],
                        "email": "test@gmail.com",
                        "exp": str(int(datetime.now().timestamp())),
                        "iat": str(int(datetime.now().timestamp())),
                        "iss": "https://cognito-idp.ap-northeast-1.amazonaws.com/ap-northeast-1_COGNITOID",
                        "token_use": "id"
                    },
                    "scopes": None
                }
            },
            "http": {
                "method": request_params['method'],
                "path": request_params['path'],
                "protocol": "HTTP/1.1",
                "sourceIp": "1.33.18.206",
                "userAgent": "PostmanRuntime/7.26.8"
            },
            "requestId": "aj8PTi-_NjMEPFQ=",
            "routeKey": "{method} {path}".format(method=request_params['method'], path=request_params['path']),
            "stage": "$default",
            "time": "11/Feb/2021:03:40:30 +0000",
            "timeEpoch": int(datetime.now().timestamp())
        },
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
            "title": "件名A",
            "content": "内容A",
            "is_done": True,
            "priority": "high",
            "created_at": 1614342166.0,
            "updated_at": 1614342166.0
        }),
        'isBase64Encoded': False
    }
