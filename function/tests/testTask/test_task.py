import pytest
from copy import deepcopy
from task import Task, TaskNotFoundError, NotTaskOwnerError
from jsonschema import ValidationError
from decimal import Decimal
import os
import boto3

DUMMY_ULID = 'ABCDEFGHIJKLMNOPQRSTUVW999'

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


@pytest.fixture(params=[
    {
        "priority": priority,
        "is_done": is_done
    }
    for priority in ["high", "medium", "low"]
    for is_done in [True, False]
])
def typical_task(request):
    return {
        "id": "ABCDEFGHIJKLMNOPQRSTUVW000",
        "title": "タイトル",
        "owner": "latest",
        "created_at": 1614342166,
        "updated_at": 1614342166,
        "meta": "latest",
        "priority": request.param.get('priority'),
        "is_done": request.param.get('is_done'),
        "content": "内容"
    }


@pytest.fixture
def single_typical_task():
    return {
        "id": "ABCDEFGHIJKLMNOPQRSTUVW000",
        "title": "タイトル",
        "owner": "existing_user_id",
        "created_at": 1614342166,
        "updated_at": 1614342166,
        "meta": "latest",
        "priority": 'medium',
        "is_done": False,
        "content": "内容"
    }


class TestTaskConstructor:

    def test_constructor(self, typical_task):
        task = Task(**typical_task)
        assert hasattr(task, "id")
        assert hasattr(task, "title")
        assert hasattr(task, "created_at")
        assert hasattr(task, "updated_at")
        assert hasattr(task, "meta")
        assert hasattr(task, "priority")
        assert hasattr(task, "is_done")
        assert hasattr(task, "content")


class TestValidation:

    def test_valid_typical_task(self, typical_task):
        task = Task(**typical_task)
        copied_task = deepcopy(typical_task)
        assert vars(task) == copied_task

    def test_raise_title_is_blunk(self, single_typical_task):
        params = deepcopy(single_typical_task)
        params["title"] = ""
        with pytest.raises(ValidationError):
            Task(**params)

    def test_raise_title_is_none(self, single_typical_task):
        params = deepcopy(single_typical_task)
        params["title"] = None
        with pytest.raises(ValidationError):
            Task(**params)

    def test_valid_title_is_100chars(self, single_typical_task):
        params = deepcopy(single_typical_task)
        params["title"] = "a" * 100
        assert Task(**params)

    def test_raise_title_is_over_100chars(self, single_typical_task):
        params = deepcopy(single_typical_task)
        params["title"] = "a" * 101
        with pytest.raises(ValidationError):
            Task(**params)

    def test_valid_contet_is_blunk(self, single_typical_task):
        params = deepcopy(single_typical_task)
        params["content"] = ""
        assert Task(**params)

    def test_valid_contet_is_none(self, single_typical_task):
        params = deepcopy(single_typical_task)
        params["content"] = None
        assert Task(**params)

    def test_valid_content_is_2000chars(self, single_typical_task):
        params = deepcopy(single_typical_task)
        params["content"] = "a" * 2000
        assert Task(**params)

    def test_raise_contet_is_over_2000(self, single_typical_task):
        params = deepcopy(single_typical_task)
        params["content"] = "a" * 2001
        with pytest.raises(ValidationError):
            Task(**params)

    def test_raise_is_done_is_not_bool_value(self, single_typical_task):
        params = deepcopy(single_typical_task)
        params["is_done"] = "dummy"
        with pytest.raises(ValidationError):
            Task(**params)

    def test_raise_is_done_is_not_in_enum_value(self, single_typical_task):
        params = deepcopy(single_typical_task)
        params["is_done"] = "dummy"
        with pytest.raises(ValidationError):
            Task(**params)


class TestGet:

    def test_get_existing_id(self, create_init_ddb_data):
        user_id = "existing_user_id"
        task_id = "ABCDEFGHIJKLMNOPQRSTUVW000"
        response = Task.get(
            user_id,
            task_id
        )
        assert vars(response) == {
            "id": "ABCDEFGHIJKLMNOPQRSTUVW000",
            "title": "件名A",
            "created_at": Decimal("1614870000.0"),
            "updated_at": Decimal("1614870000.0"),
            "meta": "latest",
            'owner': 'existing_user_id',
            "priority": "high",
            "is_done": True,
            "content": "内容A"
        }

    def test_raise_exsiting_and_not_owned_task(self, create_init_ddb_data):
        user_id = "existing_user_id"
        task_id = "ABCDEFGHIJKLMNOPQRSTUVW024"
        with pytest.raises(NotTaskOwnerError):
            Task.get(
                user_id,
                task_id
            )

    def test_raise_not_existing_id(self, create_init_ddb_data):
        user_id = "dummy_user_id"
        task_id = "DUMMY_TASK_ID"
        with pytest.raises(TaskNotFoundError):
            Task.get(
                user_id,
                task_id
            )


class TestSave:
    def test_save_new_typical_task(self, create_init_ddb_data, ulid_mock):
        temp_task = Task(**{
            "id": None,
            "title": "件名A",
            "meta": "latest",
            'owner': 'existing_user_id',
            "priority": "high",
            "is_done": True,
            "content": "内容A"
        })
        temp_task.save()
        item = table.get_item(
            Key={
                'id': 'Task:ABCDEFGHIJKLMNOPQRSTUVW999',
                'meta': 'latest'
            }
        )
        assert item['Item'] == {
            "id": "Task:ABCDEFGHIJKLMNOPQRSTUVW999",
            "meta": "latest",
            "title": "件名A",
            "owner": "existing_user_id",
            "content": "内容A",
            "is_done": True,
            "priority": "high",
            "created_at": Decimal("1614870000"),
            "updated_at": Decimal("1614870000")
        }

    def test_save_existed_typical_task(self, create_init_ddb_data, ulid_mock):
        temp_task = Task(**{
            'id': 'ABCDEFGHIJKLMNOPQRSTUVW000',
            'title': '更新タイトル',
            'priority': 'low',
            'owner': 'existing_user_id',
            'is_done': False,
            'content': '更新内容',
            'created_at': 1614870000
        })
        temp_task.save('existing_user_id')
        item = table.get_item(
            Key={
                'id': 'Task:ABCDEFGHIJKLMNOPQRSTUVW000',
                'meta': 'latest'
            }
        )
        assert item['Item'] == {
            "id": "Task:ABCDEFGHIJKLMNOPQRSTUVW000",
            "meta": "latest",
            "title": "更新タイトル",
            "owner": "existing_user_id",
            "content": "更新内容",
            "is_done": False,
            "priority": "low",
            "created_at": Decimal("1614870000"),
            "updated_at": Decimal("1614870000")
        }

    def test_raise_not_owner_task(self, create_init_ddb_data, ulid_mock):
        temp_task = Task(**{
            'id': 'ABCDEFGHIJKLMNOPQRSTUVW000',
            'title': '更新タイトル',
            'priority': 'low',
            'owner': 'existing_user_id',
            'is_done': False,
            'content': '更新内容',
            'created_at': 1614870000
        })
        with pytest.raises(NotTaskOwnerError):
            temp_task.save('not_owner_id')


class TestDelete:

    def test_delete_existing_task(self, create_init_ddb_data):
        user_id = 'existing_user_id'
        task_id = 'ABCDEFGHIJKLMNOPQRSTUVW000'
        temp_task = Task.get(user_id, task_id)
        response = temp_task.delete(user_id)
        assert response == {
            'id': 'ABCDEFGHIJKLMNOPQRSTUVW000',
            'title': '件名A',
            'owner': 'existing_user_id',
            'created_at': 1614870000.0,
            'updated_at': 1614870000.0,
            'meta': 'latest',
            'priority': 'high',
            'is_done': True,
            'content': '内容A'
        }

    def test_raise_delete_not_owner_task(self, create_init_ddb_data):
        user_id = 'not_owner_user_id'
        task_id = 'ABCDEFGHIJKLMNOPQRSTUVW000'
        with pytest.raises(NotTaskOwnerError):
            temp_task = Task.get(user_id, task_id)
            temp_task.delete(user_id)


class TestSearch:

    def test_default_search(self, create_init_ddb_data):
        """
        全48件のうち、ownerが'existing_user_id'である24件
        """
        user_id = 'existing_user_id'
        tasks = Task.search(user_id)
        assert all([x['owner'] == user_id for x in tasks])

    @pytest.mark.parametrize("word", ['A', '内容', ''])
    def test_freeeword_search(self, word, create_init_ddb_data):
        user_id = 'existing_user_id'
        tasks = Task.search(user_id, freeword=word)
        assert all([
            (word in x['title'] or word in x['content'])
            and x['owner'] == user_id
            for x in tasks
        ])

    @pytest.mark.parametrize("is_done", ['true', 'false'])
    def test_is_done_search(self, is_done, create_init_ddb_data):
        def __convert_is_done(is_done: str):
            if is_done == 'true':
                return True
            elif is_done == 'false':
                return False
        user_id = 'existing_user_id'
        tasks = Task.search(user_id, is_done=is_done)
        assert all([
            x['is_done'] is __convert_is_done(is_done) and x['owner'] == user_id for x in tasks
        ])

    @pytest.mark.parametrize("priority", ['high', 'medium', 'low'])
    def test_priority_search(self, priority, create_init_ddb_data):
        user_id = 'existing_user_id'
        tasks = Task.search(user_id, priority=priority)
        assert all([
            x['priority'] == priority and x['owner'] == user_id for x in tasks
        ])

    @pytest.mark.parametrize("word,is_done,priority", [
        (w, d, p)
        for w in ['A', '内容', '']
        for d in ['true', 'false']
        for p in ['high', 'medium', 'low']
    ])
    def test_multi_search(self, word, is_done, priority, create_init_ddb_data):
        user_id = 'existing_user_id'
        tasks = Task.search(
            user_id,
            freeword=word,
            priority=priority,
            is_done=is_done
        )
        if is_done == 'true':
            converted_is_done = True
        elif is_done == 'false':
            converted_is_done = False
        assert all([
            (word in x['title'] or word in x['content'])
            and x['is_done'] is converted_is_done
            and x['priority'] == priority
            and x['owner'] == user_id
            for x in tasks
        ])
