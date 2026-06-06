import aiofiles


async def file_read(path: str) -> str:
    """读取文件内容。"""
    try:
        async with aiofiles.open(path, "r") as f:
            return await f.read()
    except Exception as e:
        return f"Error reading file '{path}': {e}"


async def file_write(path: str, content: str) -> str:
    """写入文件。"""
    try:
        async with aiofiles.open(path, "w") as f:
            await f.write(content)
        return f"Successfully written to '{path}'"
    except Exception as e:
        return f"Error writing file '{path}': {e}"
