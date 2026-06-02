from unittest import result
import pytest
import D4
from pydantic import ValidationError
import asyncio
from unittest.mock import Mock, AsyncMock

@pytest.mark.parametrize(
    "items, size, expected",
    [
        ([], 3, []),                                    # 用例1:空列表
        ([1, 2], 3, [[1, 2]]),                          # 用例2:不足一批
        ([1, 2, 3], 3, [[1, 2, 3]]),                    # 用例3:恰好一批
        ([1, 2, 3, 4, 5, 6, 7], 3, [[1, 2, 3], [4, 5, 6], [7]]),   # 用例4:有余数 
        ([1, 2, 3], 1, [[1], [2], [3]]),
    ],
)
def test_batch_iter(items, size, expected):
    assert list(D4.batch_iter(items, size)) == expected

@pytest.fixture
def post_data():
    print("\n[setup] 造一条数据")
    yield {"userId": 1, "id": 1, "title": "测试标题", "body": "测试正文"}
    print("\n[teardown] 测试结束,清理")

def test_post_model(post_data):
    post = D4.Post(**post_data)
    assert post.user_id ==1
    assert post.title == "测试标题"

# pytest.raises 捕获 → 测试通过 等不到错 → 测试失败
def test_post_invalid_user_id(post_data):
    post_data["userId"] = 0
    with pytest.raises(ValidationError):
        D4.Post(**post_data)


@pytest.mark.asyncio
async def test_async_mechanics():
    await asyncio.sleep(0.01)
    assert 1 + 1 == 2
 
@pytest.mark.asyncio
async def test_fetch_with_fake_client(post_data):
    # ① 造假"响应":写剧本 —— 调 json() 就返回 fixture 里那条数据
    fake_resp = Mock()
    fake_resp.json.return_value = post_data

    # ② 造假"客户端":get 会被 await,所以必须用 AsyncMock
    fake_client = AsyncMock()
    fake_client.get.return_value = fake_resp

    # ③ 假客户端直接传进去 —— 不碰任何真实网络
    result = await D4.fetch(fake_client, "/posts/1")

    # ④ 验证返回值 + 取证:它确实用正确的参数调过 get
    assert result == post_data
    fake_client.get.assert_called_once_with("/posts/1")


@pytest.mark.asyncio
async def test_fetch_posts(mocker, post_data):       # mocker 是 pytest-mock 给的 fixture
    # 手术:把 D4 命名空间里的 "fetch" 换成假货
    fake_fetch = mocker.patch("D4.fetch")
    fake_fetch.return_value = post_data               # 剧本:每次被调都返回这条数据

    result = await D4.fetch_posts([1, 2, 3])

    assert len(result) == 3                           # 3 个 id → 3 个 Post
    assert all(isinstance(p, D4.Post) for p in result)
    assert fake_fetch.call_count == 3                 # 取证:fetch 被调了 3 次

@pytest.mark.asyncio
async def test_fetch_posts_error_isolation(mocker, post_data):
    fake_fetch = mocker.patch("D4.fetch")
    post_data_1 = post_data
    post_data_3 = post_data.copy()
    post_data_3["userId"] = 2
    fake_fetch.side_effect = [post_data_1, Exception("测试失败"), post_data_3]

    result = await D4.fetch_posts([1,2,3])

    assert len(result) == 2
    assert all(isinstance(p, D4.Post) for p in result)
    assert fake_fetch.call_count == 3 

