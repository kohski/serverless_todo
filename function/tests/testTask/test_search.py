import pytest
from datetime import datetime
from search import lambda_handler


@pytest.mark.parametrize("word,is_done,priority", [
    (w, d, p)
    for w in ['A', '内容', '']
    for d in ['true', 'false']
    for p in ['high', 'medium', 'low']
])
def test_valid_search(word, is_done, priority, context):
    username = 'existing_user_id'
    query_string = '?freeword={word}&is_done={is_done}&priority={priority}'.format(
        word=word, is_done=is_done, priority=priority)
    event = {
        "resource": "/task/{task_id}",
        "path": "/task{}".format(query_string),
        "httpMethod": "GET",
        "headers": {},
        "multiValueHeaders": {},
        "queryStringParameters": {
            "freeword": word,
            "is_done": is_done,
            "priority": priority
        },
        "multiValueQueryStringParameters": None,
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
                    "cognito:username": username,
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
    response = lambda_handler(event, context)
    del response['body']
    assert response == {
        'statusCode': 200,
        'isBase64Encoded': False
    }
