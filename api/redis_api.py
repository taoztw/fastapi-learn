from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/index")
async def index(request: Request):
    key = 'tz'
    # 设置缓存数据
    await request.app.state.redis_client.set(key,"测试数据")
    # 读取缓存数据
    cache1 = await request.app.state.redis_client.get(key)

    key_2 = 'tz2'
    # 添加数据，5秒后自动清除
    await request.app.state.redis_client.setex(name=key_2, time=5, value="测试数据2")
    # 测试2缓存数据的获取
    cache2 = await request.app.state.redis_client.get(key_2)
    return {
        "cache1":cache1,
        "cache2": cache2,
    }


@router.get("/index2")
async def index2(request: Request):
    async with request.app.state.redis_client.pipeline(transaction=True) as pipe:
        ok1, ok2 = await (pipe.set("xiaozhong", "测试数据").set("xiaozhong_2", "测试数据2").execute())
        pass
    async with request.app.state.redis_client.pipeline(transaction=True) as pipe:
        cache1, cache2 = await (pipe.get("xiaozhong").get("xiaozhong_2").execute())
        print(cache1, cache2)
    return {
        "cache1":cache1,
        "cache2": cache2,
    }