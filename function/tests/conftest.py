import pytest
import moto
import boto3
import os


DEFAULT_TIME = '2021-03-04T15:00:00'

env = {
    "TABLE_NAME": "DummyTable"
}

for k in env:
    os.environ[k] = env[k]


@pytest.fixture(autouse=True)
@pytest.mark.freeze_time
def set_time(freezer):
    freezer.move_to(DEFAULT_TIME)


@pytest.fixture(autouse=True)
def start_ddb_moto_mock():
    moto.mock_dynamodb2().start()
    yield
    moto.mock_s3().stop()


@pytest.fixture(autouse=True)
def ddb_setup(start_ddb_moto_mock):
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
            }
        ]
    )


@pytest.fixture(autouse=True)
def create_init_ddb_data(
    ddb_setup
):
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
        "aaaaaaaa-aaaa-aaaa-aaaa-111111111111",
        "bbbbbbbb-bbbb-bbbb-bbbb-222222222222"
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
        for p in PRIORITY_LIST
        for d in IS_DONE_LIST
        for u in USER_ID_LIST
        for t in TITLE_LIST
        for c in CONTENT_LIST
    ]

    for id, item in enumerate(db_items):
        item = {
            "id": "Task:{}:ABCDEFGHIJKLMNOPQRSTUVWXYZ{}".format(item['user_id'], str(id).zfill(3)),
            "title": item['title'],
            "created_at": 1614342166,
            "updated_at": 1614342166,
            "meta": 'latest',
            "priority": item['priority'],
            "is_done": item['is_done'],
            "content": item['content']
        }
        table.put_item(Item=item)
