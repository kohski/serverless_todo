import pytest
import moto
import boto3
import os
from datetime import datetime
from decimal import Decimal


DEFAULT_TIME = '2021-03-04T15:00:00'

env = {
    "TABLE_NAME": "DummyTable",
    "USER_POOL_NAME": "UserPoolId",
    "CLIENT_NAME": "ClientId"
}

for k in env:
    os.environ[k] = env[k]


@pytest.fixture(autouse=True)
@pytest.mark.freeze_time
def set_time(freezer):
    freezer.move_to(DEFAULT_TIME)


@pytest.fixture(autouse=True)
def start_moto_mock():
    moto.mock_dynamodb2().start()
    moto.mock_cognitoidp().start()
    yield
    moto.mock_cognitoidp().stop()
    moto.mock_dynamodb2().stop()


@pytest.fixture(autouse=True)
def ddb_setup(start_moto_mock):
    dynamodb = boto3.resource('dynamodb')
    dynamodb.create_table(
        TableName=os.environ['TABLE_NAME'],
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'meta',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "id",
                "AttributeType": "S"
            },
            {
                "AttributeName": "meta",
                "AttributeType": "S"
            },
            {
                "AttributeName": "owner",
                "AttributeType": "S"
            }
        ],
        BillingMode='PAY_PER_REQUEST',
        GlobalSecondaryIndexes=[
            {
                "IndexName": "meta-id-index",
                "KeySchema": [
                    {
                        "AttributeName": "meta",
                        "KeyType": "HASH"
                    },
                    {
                        "AttributeName": "id",
                        "KeyType": "RANGE"
                    }
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                }
            },
            {
                "IndexName": "owner-meta-index",
                "KeySchema": [
                    {
                        "AttributeName": "owner",
                        "KeyType": "HASH"
                    },
                    {
                        "AttributeName": "meta",
                        "KeyType": "RANGE"
                    }
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                }
            }
        ]
    )


users = [
    {
        "id": "existing_user_id",
        "given_name": "テスト",
        "family_name": "ユーザー",
        "email": "test@test.com",
        "password": "Test1234#",
        "email_verified": "true"
    }
]


@pytest.fixture(autouse=True)
def create_init_ddb_data(ddb_setup, set_time):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])

    PRIORITY_LIST = [
        "high",
        "medium",
        "low"
    ]

    IS_DONE_LIST = [
        True,
        False
    ]

    USER_ID_LIST = [
        "existing_user_id",
        "other_user_id"
    ]

    TITLE_LIST = [
        "件名A",
        "件名B"
    ]

    CONTENT_LIST = [
        "内容A",
        "内容B"
    ]

    db_items = [
        {
            "priority": p,
            "is_done": d,
            "user_id": u,
            "title": t,
            "content": c
        }
        for u in USER_ID_LIST
        for t in TITLE_LIST
        for p in PRIORITY_LIST
        for d in IS_DONE_LIST
        for c in CONTENT_LIST
    ]

    for id, item in enumerate(db_items):
        item = {
            "id": "Task:ABCDEFGHIJKLMNOPQRSTUVW{}".format(str(id).zfill(3)),
            "title": item['title'],
            "owner": item['user_id'],
            "created_at": Decimal(datetime.now().timestamp()),
            "updated_at": Decimal(datetime.now().timestamp()),
            "meta": "latest",
            "priority": item['priority'],
            "is_done": item['is_done'],
            "content": item['content']
        }
        table.put_item(Item=item)


@pytest.fixture(autouse=True)
def idp_setup(start_moto_mock):
    idp = boto3.client('cognito-idp')
    userpool = idp.create_user_pool(
        PoolName=env['USER_POOL_NAME'],
        Policies={
            'PasswordPolicy': {
                'MinimumLength': 6,
                'RequireUppercase': True,
                'RequireLowercase': True,
                'RequireNumbers': True,
                'RequireSymbols': True,
                'TemporaryPasswordValidityDays': 7
            }
        },
        AutoVerifiedAttributes=[
            'email'
        ],
        AliasAttributes=[
            'username',
            'email'
        ],
        AdminCreateUserConfig={
            'AllowAdminCreateUserOnly': True,
        },
        Schema=[
            {
                'Name': 'email',
                'Required': True
            },
            {
                'Name': 'given_name',
                'Required': True
            },
            {
                'Name': 'family_name',
                'Required': True
            }
        ]
    )
    os.environ['USER_POOL_ID'] = userpool['UserPool']['Id']

    client = idp.create_user_pool_client(
        UserPoolId=userpool['UserPool']['Id'],
        ClientName=os.environ["CLIENT_NAME"],
        ExplicitAuthFlows=[
            'ADMIN_NO_SRP_AUTH'
        ]
    )
    os.environ['CLIENT_ID'] = client['UserPoolClient']['ClientId']


@pytest.fixture()
def idp_create_init_data(idp_setup):
    # 初期データの作成
    idp = boto3.client('cognito-idp')

    for user in users:
        param = {
            'UserPoolId': os.environ['USER_POOL_ID'],
            'Username': user["id"],
            'UserAttributes': [
                {
                    'Name': 'given_name',
                    'Value': user['given_name']
                },
                {
                    'Name': 'family_name',
                    'Value': user['family_name']
                },
                {
                    'Name': 'email',
                    'Value': user['email']
                },
                {
                    'Name': 'email_verified',
                    'Value': user['email_verified']
                }
            ],
            'DesiredDeliveryMediums': [
                'EMAIL',
            ],
            'TemporaryPassword': user["password"]
        }
        idp.admin_create_user(**param)
        res = idp.admin_initiate_auth(
            UserPoolId=os.environ['USER_POOL_ID'],
            ClientId=os.environ['CLIENT_ID'],
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': user["id"],
                'PASSWORD': user["password"]
            }
        )

        idp.respond_to_auth_challenge(
            ClientId=os.environ['CLIENT_ID'],
            ChallengeName='NEW_PASSWORD_REQUIRED',
            ChallengeResponses={
                'NEW_PASSWORD': user["password"],
                'USERNAME': user["id"],
                'userAttributes.given_name': user['given_name'],
                'userAttributes.family_name': user['family_name'],
                'userAttributes.email': user['email']
            },
            Session=res['Session']
        )
