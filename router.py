from fastapi import APIRouter
from api.parameter import router as parameter_router
from api.exception import router as exception_router
from api.user import router as user_router
from api.redis_api import router as redis_router
from api.oauth2_test.oauth2_mode_client import router as oauth2_mode_client_router
from api.oauth2_test.oauth2_mode_password import router as oauth2_mode_password_router

router = APIRouter()

router.include_router(parameter_router, prefix="/parameter", tags=["参数校验"])
router.include_router(exception_router, prefix="/exception", tags=["异常"])
router.include_router(user_router, prefix="/user", tags=["用户操作"])
router.include_router(redis_router, prefix="/redis", tags=["redis缓存操作"])
router.include_router(oauth2_mode_client_router, tags=["oauth2客户端模式"])
router.include_router(oauth2_mode_password_router, tags=["oauth2密码模式"])

