from fastapi import APIRouter, UploadFile
from fastapi import Path, Query, Body, Form, File, Header, Request, Response, Cookie, status
from enum import Enum
from typing import Optional
from typing import List
from pydantic import BaseModel, Field
import aiofiles

router = APIRouter()


@router.get("/path/{user_id}/article/{article_id}", summary="路径Path参数")
async def parameter_test(user_id: int, article_id: int):
    return {"user_id": user_id, "article_id": article_id}


@router.get("/path/uls/{file_path:path}", summary="路径参数-带/路径的参数")
async def parameter_test(file_path: str):
    return {"file_path": file_path}


# 枚举
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"
@router.get("/path/enum/{model_name}", summary="路径参数-枚举参数")
async def parameter_test(model_name: ModelName):
    return {"model_name": model_name}


@router.get("/path/custom/{user_id}/article/{article_id}", summary="路径参数-路径参数的更多检验")
async def parameter_test(
    user_id: int = Path(..., title="用户ID", description="用户ID信息", ge=1, le=1000),
    article_id: str = Path(..., title="文章ID", max_length=100, min_length=2)
):
    return {"user_id": user_id, "article_id": article_id}


# Query参数
# /items/?skip=0&limit=10 skip和limit是Query参数
@router.get("/query/", summary="Query参数-Query参数的基本使用")
async def parameter_query(user_id: int, is_admin: bool=False, user_name: Optional[str]=None, user_token: str = "token"):
    return {"user_id": user_id, "user_name": user_name, "user_token": user_token}


@router.get("/query/custom", summary="Query参数-参数多条件校验")
async def parameter_query(
    user_id: int = Query(...,ge=10, le=100),
    user_name: str = Query("tz", min_length=1, max_length=200)
):
    return {"user_id": user_id, "user_name": user_name}


@router.get("/query/list", summary="Query参数-List多值查询")
async def parameter_query(
    user_name: List[str] = Query(["test", "test2"])
):
    return {"user_name": user_name}



@router.post("/body/", summary="Body参数-Body参数的基本使用")
async def parameter_body(
    token: str = Body(None),
    user_id: int = Body(..., ge=1),
    ):
    return {"token": token, "user_id": user_id}


class Item(BaseModel):
    token: str = Field(None, title="用户token", description="用户token信息")
    timestamp: int

@router.post("/body/basemodel/", summary="Body参数-BaseModel 使用")
async def parameter_body(item: Item=Body(..., embed=True)):
    return {"token": item.token, "user_id": item.timestamp}


# Form
@router.post("/form/", summary="Form参数-Form参数的基本使用")
async def parameter_form(
    username: str = Form(...,description="用户账号"),
    password: str = Form(...,description="用户密码"),
    ):
    return {"token": username, "user_id": password}


# Form 文件上传
@router.post("/form/file/", summary="Form参数-Form文件上传")
async def parameter_form(
    file: bytes = File(...),  # 会将整个文件读取在内存中然后写入，只适用于小文件场景。
    ):
    # 异步方式写入文件
    async with aiofiles.open("./test.txt", "wb") as f:
        await f.write(file)

    return {"file_size": len(file)}


# fastapi提供了更高级的文件上传
@router.post("/form/file/advanced/", summary="Form参数-Form文件上传")
async def parameter_form(
    file: UploadFile = File(...),  # 当占用的内存达到阈值后，将文件保存在磁盘中，UploadFile包含文件的很多元数据
    ):
    content = await file.read()
    with open("./test.txt", "wb") as f:
        f.write(content)
    return {"filename": file.filename, "content_type": file.content_type, "file_size": len(content)}




# Header 参数
@router.get("/header/", summary="Header参数-Header参数的基本使用")
async def parameter_header(
    user_agent: Optional[str] = Header(None, convert_underscores=True),
    # 设置convert_underscores=True，可以将header中的下划线转换为中划线
    x_token: List[str] = Header(None),
    ):
    return {"user_agent": user_agent, "x_token": x_token}


# Cookie
@router.post("/cookie/set", summary="Cookie参数-设置Cookie")
async def set_cookie(response: Response):
    response.set_cookie(key="token", value="cookie-value")
    return "nice"


@router.get("/cookie/get", summary="Cookie参数-获取Cookie")
async def get_cookie(token: Optional[str] = Cookie(None)):
    return {"token": token}



@router.get("/request/", summary="Request参数-Request参数的基本使用")
async def test_request(request: Request):
    form_data = await request.form()
    body_data = await request.body()
    return {"client_host": request.client.host, "headers": request.headers}

@router.get("/response/404", summary="Response参数-Response参数的基本使用")
async def test_response(response: Response):
    response.status_code = status.HTTP_404_NOT_FOUND
    # 自定义Response
    # return Response(content="hello", media_type="text/plain", headers={"X-Cat": "meow"})
    return {"message": "hello"}