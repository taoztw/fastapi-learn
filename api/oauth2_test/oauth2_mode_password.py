from datetime import datetime, timedelta
from typing import Optional, Dict

from fastapi import Query, Depends
from fastapi.security import OAuth2, OAuth2PasswordBearer
from fastapi import APIRouter
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, JWTError
from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status
from pydantic import ValidationError
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from common.oauth_utils import TokenUtils

router = APIRouter()


fake_users_db = {
    "xiaozhong": {
        "username": "xiaozhong",
        "full_name": "xiaozhong tongxue",
        "email": "xiaozhong@example.com",
        "password": "123456",
        "disabled": False,
    },
}

# 微信第三方客户端数据表信息
fake_client_db = {
    "xiaozhong": {
        "client_id": "xiaozhong",
        "client_secret": "123456",
    }
}

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/connect/oauth2/authorize")


@router.post("/connect/oauth2/authorize", summary="请求授权URL地址")
async def login(user_form_data: OAuth2PasswordRequestForm = Depends()):
    if not user_form_data:
        raise HTTPException(status_code=400, detail="请输入用户账号及密码等信息")

    if not user_form_data.client_id and not user_form_data.client_secret:
        raise HTTPException(status_code=400, detail="请输入分配给第三方APPID及秘钥等信息")

    userinfo = fake_users_db.get(user_form_data.username)
    if user_form_data.username not in fake_users_db:
        raise HTTPException(status_code=400, detail="不存在此用户信息", headers={"WWW-Authenticate": f"Bearer"})

    if user_form_data.password != userinfo.get('password'):
        raise HTTPException(status_code=400, detail="用户密码不对")

    clientinfo = fake_client_db.get(user_form_data.client_id)
    if user_form_data.client_id not in fake_client_db:
        raise HTTPException(status_code=400, detail="非法第三方客户端APPID", headers={"WWW-Authenticate": f"Bearer"})

    if user_form_data.client_secret != clientinfo.get('client_secret'):
        raise HTTPException(status_code=400, detail="第三方客户端部秘钥不正确!")

    data = {
        'iss ': user_form_data.username,
        'sub': 'xiaozhongtongxue',
        'username': user_form_data.username,
        'admin': True,
        'exp': datetime.utcnow() + timedelta(minutes=15)
    }

    token = TokenUtils.token_encode(data=data)

    return {"access_token": token, "token_type": "bearer"}


# token依赖的接口，需要用户名和密码验证
@router.get("/connect/user/password", summary="请求用户信息地址（受保护资源）")
async def get_user_password(token: str = Depends(oauth2_scheme)):
    payload = TokenUtils.token_decode(token=token)
    # 定义认证异常信息
    username = payload.get('username')
    if username not in fake_users_db:
        raise HTTPException(status_code=400, detail="不存在此用户信息", headers={"WWW-Authenticate": f"Bearer"})

    userinfo = fake_users_db.get(username)

    return {'info': {
        'username': username,
        'password': userinfo.get('password')
    }}
