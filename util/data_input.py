from boto3.session import Session
from decimal import Decimal
import math
import ulid
from datetime import datetime
import time
from decimal import Decimal
import random


def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        if math.modf(obj)[0] == 0.0:
            return int(obj)
        else:
            return float(obj)
    raise Exception


profile = 'im-manage'
session = Session(profile_name=profile)

dynamodb = session.resource('dynamodb')
table = dynamodb.Table('serverless-todo-TaskTable22070546-18OMCGJ99D0QC')

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
    "test_user",
    "other_user"
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
        "owner": u,
        "title": t,
        "content": c
    }
    for u in USER_ID_LIST
    for t in TITLE_LIST
    for p in PRIORITY_LIST
    for d in IS_DONE_LIST
    for c in CONTENT_LIST
]


for item in db_items:
    task_id = str(ulid.new())
    item['id'] = 'Task:' + task_id
    item['meta'] = 'latest'
    duration_craeted = random.randint(1, 10000)
    duration_updated = random.randint(1, 10000)
    item['created_at'] = Decimal(
        int(datetime.now().timestamp()) - duration_craeted - duration_updated)
    item['updated_at'] = Decimal(
        int(datetime.now().timestamp()) - duration_craeted)
    table.put_item(
        Item=item
    )
    print(item)
