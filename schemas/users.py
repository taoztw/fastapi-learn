from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    """
    创建用户记录时需要传递的参数信息
    """
    name: str
    password: str
    nikename: str
    email: str
