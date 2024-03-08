import time

from fastapi import FastAPI
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
import pathlib
import threading
import aioredis
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from base_middleware.base_middleware import AuthMiddleware, TracedIDMiddleware, request_context
from router import router as api_router
from services.user import UserServeries


# 替代startup shutdown写法
@asynccontextmanager
async def lifespan(app: FastAPI):
    await UserServeries.init_create_table()
    app.state.redis_client = aioredis.from_url(REDIS_URL, encoding="utf-8",decode_responses=True)
    yield

    app.state.redis_client.close()
    print("关闭后执行")
app = FastAPI(
    title="学习Fastapi框架",
    description="介绍和描述",
    version="0.0.1",
    debug=False,
    lifespan=lifespan,
    docs_url=None,  # 使用自定义css js资源 swagger文档时，需要将docs设置为None
    # openapi_url=False,
    terms_of_service="https://tz.life",
    contact={
        "name": "Tz",
        "url":"https://tz/life",
        "email": "tztw4723@gmail.com"
    },
    license_info={
        "name": "版权信息说明",
        "url": "https://tz.life"
    },
    openapi_tags=[
        {"name": "接口分组",
         "description": "接口分组信息说明"}
    ],
    servers=[
        {"url": "/", "description": "本地调试环境"},
        {"url": "/dev", "description": "线上测试环境"},
        {"url": "/online", "description": "线上生产环境"},
    ]
)

from core_setting import REDIS_URL



templates = Jinja2Templates(directory=f"{pathlib.Path.cwd()}/templates/")
staticfiles = StaticFiles(directory=f"{pathlib.Path.cwd()}/static")
app.mount("/static",staticfiles, name='static')

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png"
    )


@app.get("/app/hello", tags=["app实例对象注册接口示例"])
def app_hello():
    print(f"当前同步函数运行的线程ID: {threading.current_thread().ident}")
    # print("跟踪id",request.state.traceid)
    request = request_context.get()
    print("跟踪id request_context", request.state.traceid)
    return {"hello": "app"}


@app.get("/", response_class=HTMLResponse)
async def get_response(request: Request):
    print(f"当前异步函数运行的线程ID: {threading.current_thread().ident}")
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(api_router, prefix="/api")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def request_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"code": 400, "message": str(exc)}
    )


"""
中间件配置
"""
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(process_time)
    return response

app.add_middleware(AuthMiddleware, header_value="CustomAuth")
app.add_middleware(TracedIDMiddleware)


# 废弃
# @app.on_event("startup")
# async def startup_event():
#     await UserServeries.init_create_table()
#
# @app.on_event("shutdown")
# async def shutdown():
#     pass





if __name__ == '__main__':
    import os
    import uvicorn
    app_model_name = os.path.basename(__file__).replace(".py","")
    uvicorn.run(f"{app_model_name}:app",host="127.0.0.1", reload=True)