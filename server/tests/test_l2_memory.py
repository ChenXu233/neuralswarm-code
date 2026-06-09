import pytest

from neuralswarm.services.memory.l2_memory import L2Memory, Knowledge


@pytest.fixture
def l2_memory():
    return L2Memory()


async def test_store_knowledge(l2_memory):
    """测试存储知识"""
    knowledge = await l2_memory.store_knowledge(
        project_id="proj-1",
        content="Python 是一种解释型语言",
        source="documentation"
    )

    assert isinstance(knowledge, Knowledge)
    assert knowledge.content == "Python 是一种解释型语言"
    assert knowledge.source == "documentation"
    assert knowledge.project_id == "proj-1"
    assert knowledge.metadata == {}


async def test_store_knowledge_with_metadata(l2_memory):
    """测试带元数据的知识存储"""
    metadata = {"category": "programming", "importance": "high"}

    knowledge = await l2_memory.store_knowledge(
        project_id="proj-1",
        content="Django 是一个 Web 框架",
        source="tutorial",
        metadata=metadata
    )

    assert knowledge.metadata == metadata


async def test_search_knowledge(l2_memory):
    """测试搜索知识"""
    await l2_memory.store_knowledge("proj-1", "Python 是一种编程语言", "docs")
    await l2_memory.store_knowledge("proj-1", "Java 也是一种编程语言", "docs")
    await l2_memory.store_knowledge("proj-1", "Web 开发框架", "tutorial")

    results = await l2_memory.search_knowledge("proj-1", "编程")

    assert len(results) == 2
    assert all("编程" in k.content for k in results)


async def test_search_knowledge_case_insensitive(l2_memory):
    """测试搜索知识大小写不敏感"""
    await l2_memory.store_knowledge("proj-1", "Python Programming", "docs")

    results = await l2_memory.search_knowledge("proj-1", "python")

    assert len(results) == 1
    assert results[0].content == "Python Programming"


async def test_search_knowledge_returns_empty_for_no_match(l2_memory):
    """测试搜索无匹配结果返回空列表"""
    await l2_memory.store_knowledge("proj-1", "Python 是一种编程语言", "docs")

    results = await l2_memory.search_knowledge("proj-1", "Java")

    assert results == []


async def test_search_knowledge_returns_empty_for_unknown_project(l2_memory):
    """测试搜索不存在项目的知识返回空列表"""
    results = await l2_memory.search_knowledge("nonexistent", "Python")

    assert results == []


async def test_search_knowledge_with_limit(l2_memory):
    """测试搜索知识数量限制"""
    for i in range(10):
        await l2_memory.store_knowledge("proj-1", f"知识条目 {i}: Python 编程", "docs")

    results = await l2_memory.search_knowledge("proj-1", "Python", limit=3)

    assert len(results) == 3


async def test_search_knowledge_project_isolation(l2_memory):
    """测试不同项目的知识互相隔离"""
    await l2_memory.store_knowledge("proj-1", "项目1的 Python 知识", "docs")
    await l2_memory.store_knowledge("proj-2", "项目2的 Java 知识", "docs")

    results_1 = await l2_memory.search_knowledge("proj-1", "Python")
    results_2 = await l2_memory.search_knowledge("proj-2", "Java")

    assert len(results_1) == 1
    assert len(results_2) == 1
    assert results_1[0].project_id == "proj-1"
    assert results_2[0].project_id == "proj-2"


async def test_get_all_knowledge(l2_memory):
    """测试获取项目所有知识"""
    await l2_memory.store_knowledge("proj-1", "知识A", "source_a")
    await l2_memory.store_knowledge("proj-1", "知识B", "source_b")
    await l2_memory.store_knowledge("proj-1", "知识C", "source_c")

    knowledge_list = await l2_memory.get_all_knowledge("proj-1")

    assert len(knowledge_list) == 3
    assert knowledge_list[0].content == "知识A"
    assert knowledge_list[1].content == "知识B"
    assert knowledge_list[2].content == "知识C"


async def test_get_all_knowledge_returns_empty_for_unknown_project(l2_memory):
    """测试获取不存在项目的知识返回空列表"""
    knowledge_list = await l2_memory.get_all_knowledge("nonexistent")

    assert knowledge_list == []


async def test_get_all_knowledge_project_isolation(l2_memory):
    """测试不同项目的知识互相隔离"""
    await l2_memory.store_knowledge("proj-1", "项目1的知识", "docs")
    await l2_memory.store_knowledge("proj-2", "项目2的知识", "docs")

    knowledge_1 = await l2_memory.get_all_knowledge("proj-1")
    knowledge_2 = await l2_memory.get_all_knowledge("proj-2")

    assert len(knowledge_1) == 1
    assert len(knowledge_2) == 1
    assert knowledge_1[0].project_id == "proj-1"
    assert knowledge_2[0].project_id == "proj-2"


async def test_knowledge_default_metadata():
    """测试 Knowledge 数据类的默认元数据"""
    knowledge = Knowledge(
        content="测试内容",
        source="测试来源",
        project_id="proj-1"
    )

    assert knowledge.metadata == {}
