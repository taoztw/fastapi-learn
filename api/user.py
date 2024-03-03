from fastapi import APIRouter
from schemas.users import UserCreate
from db.database import AsyncSession
from dependencies.db_session import get_db_session
from fastapi import Depends
from services.user import UserServeries

router = APIRouter()

@router.post("/creat")
async def create_user(user: UserCreate, db_session: AsyncSession = Depends(get_db_session)):
    result = await UserServeries.create_user(db_session, **user.model_dump())
    return {"msg": "创建用户成功", "code": 200, "data": result}

@router.get("/info")
async def get_user_info():
    return {"msg": "获取用户信息成功", "code": 200}

@router.get("/list")
async def get_user_list():
    return {"msg": "获取用户列表成功", "code": 200}

@router.put("/edit")
async def edit_user():
    return {"msg": "编辑用户成功", "code": 200}

@router.delete("/delete")
async def delete_user():
    return {"msg": "删除用户成功", "code": 200}