import os
import tempfile

import pytest

from neuralswarm.core.tools.file_ops import create_file_ops
from neuralswarm.core.tools.shell import create_shell


@pytest.fixture
def project_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def file_ops(project_dir):
    (file_read, _), (file_write, _) = create_file_ops(project_dir)
    return file_read, file_write


@pytest.fixture
def shell_tool(project_dir):
    shell, _ = create_shell(project_dir)
    return shell


@pytest.mark.asyncio
async def test_file_read(file_ops, project_dir):
    file_read, _ = file_ops
    path = os.path.join(project_dir, "test.txt")
    with open(path, "w") as f:
        f.write("hello world")
    result = await file_read("test.txt")
    assert result == "hello world"


@pytest.mark.asyncio
async def test_file_read_absolute(file_ops, project_dir):
    file_read, _ = file_ops
    path = os.path.join(project_dir, "test.txt")
    with open(path, "w") as f:
        f.write("absolute")
    result = await file_read(path)
    assert result == "absolute"


@pytest.mark.asyncio
async def test_file_read_not_found(file_ops):
    file_read, _ = file_ops
    result = await file_read("/nonexistent/file.txt")
    assert "Error" in result


@pytest.mark.asyncio
async def test_file_write(file_ops, project_dir):
    _, file_write = file_ops
    result = await file_write("output.txt", "content")
    assert "success" in result.lower() or "written" in result.lower()
    with open(os.path.join(project_dir, "output.txt")) as f:
        assert f.read() == "content"


@pytest.mark.asyncio
async def test_file_write_subdir(file_ops, project_dir):
    _, file_write = file_ops
    result = await file_write("sub/dir/file.txt", "nested")
    assert "success" in result.lower() or "written" in result.lower()
    with open(os.path.join(project_dir, "sub", "dir", "file.txt")) as f:
        assert f.read() == "nested"


@pytest.mark.asyncio
async def test_shell_default_cwd(shell_tool, project_dir):
    result = await shell_tool("pwd" if os.name != "nt" else "cd")
    assert project_dir.replace("\\", "/") in result.replace("\\", "/")


@pytest.mark.asyncio
async def test_shell_error(shell_tool):
    result = await shell_tool("command_that_does_not_exist")
    assert "command_that_does_not_exist" in result
    assert result.strip() != ""
