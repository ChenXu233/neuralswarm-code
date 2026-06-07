from uuid import uuid4

import pytest

from neuralswarm.schemas.project import ProjectCreate, ProjectResponse
from neuralswarm.schemas.task import TaskCreate, TaskResponse


def test_project_create():
    p = ProjectCreate(name="test", path="/home/user/test")
    assert p.name == "test"


def test_project_create_validation():
    with pytest.raises(Exception):
        ProjectCreate(name="", path="/home/user/test")


def test_task_create():
    t = TaskCreate(project_id=uuid4(), prompt="hello")
    assert t.prompt == "hello"


def test_task_create_validation():
    with pytest.raises(Exception):
        TaskCreate(project_id=uuid4(), prompt="")
