import pytest
from task import Task


@pytest.fixture
def typical_task():
    return {
        "id": "Task:b3117b67-b21b-4360-bf4c-0720dcca07c3:01EZF4KKWT0E55RCA50ER4KADX",
        "title": "タイトル",
        "created_at": 1614342166.868132,
        "updated_at": 1614342166.868132,
        "meta": 'latest',
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
