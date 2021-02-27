import pytest
from copy import deepcopy
from task import Task, TaskNotFoundError
from jsonschema import ValidationError
from decimal import Decimal


PRIORITY_LIST = [
    "high",
    "medium",
    "low"
]

IS_DONE_LIST = [
    True,
    False
]


@pytest.fixture(params=PRIORITY_LIST)
def priority_params(request):
    return request.param


@pytest.fixture(params=IS_DONE_LIST)
def is_done_params(request):
    return request.param


@pytest.fixture
def typical_task(priority_params, is_done_params):
    return {
        "id": "Task:aaaaaaaa-aaaa-aaaa-aaaa-111111111111:ABCDEFGHIJKLMNOPQRSTUVW000",
        "title": "タイトル",
        "created_at": 1614342166,
        "updated_at": 1614342166,
        "meta": 'latest',
        "priority": priority_params,
        "is_done": is_done_params,
        "content": "内容"
    }


@pytest.fixture
def single_typical_task():
    return {
        "id": "Task:aaaaaaaa-aaaa-aaaa-aaaa-111111111111:ABCDEFGHIJKLMNOPQRSTUVW000",
        "title": "タイトル",
        "created_at": 1614342166,
        "updated_at": 1614342166,
        "meta": 'latest',
        "priority": 'medium',
        "is_done": False,
        "content": "内容"
    }


class TestTaskConstructor:

    def test_constructor(self, typical_task):
        print(typical_task)
        task = Task(**typical_task)
        assert hasattr(task, "id")
        assert hasattr(task, "title")
        assert hasattr(task, "created_at")
        assert hasattr(task, "updated_at")
        assert hasattr(task, "meta")
        assert hasattr(task, "priority")
        assert hasattr(task, "is_done")
        assert hasattr(task, "content")
        assert hasattr(task, "for_search")


class TestValidation:

    def test_valid_typical_task(self, typical_task):
        task = Task(**typical_task)
        copied_task = deepcopy(typical_task)
        copied_task["for_search"] = copied_task["title"] + \
            copied_task["content"]
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
        user_id = "aaaaaaaa-aaaa-aaaa-aaaa-111111111111"
        task_id = "ABCDEFGHIJKLMNOPQRSTUVWXYZ000"
        response = Task.get(
            user_id,
            task_id
        )
        assert response == {
            "id": "Task:aaaaaaaa-aaaa-aaaa-aaaa-111111111111:ABCDEFGHIJKLMNOPQRSTUVWXYZ000",
            "title": "件名A",
            "created_at": Decimal("1614342166"),
            "updated_at": Decimal("1614342166"),
            "meta": "latest",
            "priority": "high",
            "is_done": True,
            "content": "内容A"
        }

    def test_raise_not_existing_id(self, create_init_ddb_data):
        user_id = "dummy_user_id"
        task_id = "DUMMY_TASK_ID"
        with pytest.raises(TaskNotFoundError):
            Task.get(
                user_id,
                task_id
            )