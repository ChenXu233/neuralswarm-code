import os
import tempfile

import pytest

from neuralswarm.core.tools.file_ops import file_read, file_write
from neuralswarm.core.tools.shell import shell


@pytest.mark.asyncio
async def test_file_read():
    path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("hello world")
            f.flush()
            path = f.name
        result = await file_read(path)
        assert result == "hello world"
    finally:
        if path and os.path.exists(path):
            os.unlink(path)


@pytest.mark.asyncio
async def test_file_read_not_found():
    result = await file_read("/nonexistent/file.txt")
    assert "Error" in result


@pytest.mark.asyncio
async def test_file_write():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test.txt")
        result = await file_write(path, "content")
        assert "success" in result.lower() or "written" in result.lower()
        with open(path) as f:
            assert f.read() == "content"


@pytest.mark.asyncio
async def test_shell():
    result = await shell("echo hello")
    assert "hello" in result


@pytest.mark.asyncio
async def test_shell_error():
    result = await shell("command_that_does_not_exist")
    # On POSIX, exception path returns "Error executing command: ..."
    # On Windows, cmd.exe returns stderr with command-not-found message (non-ASCII)
    # In all cases, the failed command name should appear in the output and result is non-empty
    assert "command_that_does_not_exist" in result
    assert result.strip() != ""
