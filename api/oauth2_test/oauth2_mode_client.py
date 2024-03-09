from datetime import datetime, timedelta
from typing import Optional, Dict

from fastapi import Query, Depends
from fastapi.security import OAuth2
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
fake_client_db = {
    "tz": {
        "client_id": "tz",
        "client_secret": "123456",
    }
}

class OAuth2ClientCredentialsBearer(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            description: Optional[str] = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            clientCredentials={
                "tokenUrl": tokenUrl,
                "scopes": scopes,
            }
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None  # pragma: nocover
        return param


oauth2_scheme = OAuth2ClientCredentialsBearer(tokenUrl="/oauth2/authorize",scheme_name="客户端模式",description="客户端模式描述")


class OAuth2ClientCredentialsRequestForm:

    def __init__(
            self,
            grant_type: str = Query(..., regex="client_credentials"),
            scope: str = Query(""),
            client_id: str = Query(...),
            client_secret: str = Query(...),
            username: Optional[str] = Query(None),
            password: Optional[str] = Query(None),
    ):
        self.grant_type = grant_type
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password




@router.post("/oauth2/authorize", summary="请求授权URL地址")
async def authorize(client_data: OAuth2ClientCredentialsRequestForm = Depends()):
    if not client_data:
        raise HTTPException(status_code=400, detail="请输入用户账号及密码等信息")

    if not client_data.client_id and not client_data.client_secret:
        raise HTTPException(status_code=400, detail="请输入分配给第三方APPID及秘钥等信息")

    clientinfo = fake_client_db.get(client_data.client_id)
    if client_data.client_id not in fake_client_db:
        raise HTTPException(status_code=400, detail="非法第三方客户端APPID", headers={"WWW-Authenticate": f"Bearer"})

    if client_data.client_secret != clientinfo.get('client_secret'):
        raise HTTPException(status_code=400, detail="第三方客户端部秘钥不正确!")
    data = {
        'iss ': 'client_id',
        'sub': 'xiaozhongtongxue',
        'client_id': client_data.client_id,
        'exp': datetime.utcnow() + timedelta(minutes=15)
    }
    token = TokenUtils.token_encode(data=data)
    return {"access_token": token, "token_type": "bearer","exires_in":159,"scope":"all"}


# 需要授权才可以
@router.get("/get/clientinfo", summary="请求用户信息地址（受保护资源）")
async def get_clientinfo(token: str = Depends(oauth2_scheme)):
    '''
    定义API接口。改API接口需要token值并校验通过才可以访问
    :param token:
    :return:
    '''
    payload = TokenUtils.token_decode(token=token)
    # 定义认证异常信息
    client_id = payload.get('client_id')
    if client_id not in client_id:
        raise HTTPException(status_code=400, detail="不存在client_id信息", headers={"WWW-Authenticate": f"Bearer"})

    clientinfo = fake_client_db.get(client_id)

    return {'info': {
        'client_id': clientinfo.get('client_id'),
        'client_secret': clientinfo.get('client_secret')
    }}