import pydantic
from pydantic import BaseModel
from typing import List, Optional, Set, Dict, Tuple, Union

class Person(BaseModel):
    name: str
    age: int
    address: Optional[str]
    password: str


if __name__ == "__main__":
    p = Person(name="tz", age=18, address="", password="12123")
    print(p)
    print(p.dict(exclude="password"))