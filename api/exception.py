from fastapi import APIRouter, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi import Query, Body

router = APIRouter()




@router.get("/exception", summary="异常处理-HTTPException")
async def exception_test(admin: str = Query(default="admin")):
    if admin == "admin":
        raise HTTPException(status_code=403, detail="你没有权限")

    return {"code": 200}


"""
中间件异常会最终抛出 Exception, 所以捕获中间件异常需要直接捕获Exception
顶层ServerErrorMiddleware会最终捕获中间件异常并抛出Exception
"""


@router.post("/exception/valid", summary="异常处理-HTTPException")
async def exception_test(num: int=Body(...)):

    return {"code": 200}
