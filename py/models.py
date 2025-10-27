from pydantic import BaseModel, EmailStr
from typing import Dict, List

class DayRecord(BaseModel):
    date: str
    money: int
    north: Dict[str, int]
    lim: Dict[str, int]
    bp_level: int
    bp_exp: int

class User(BaseModel):
    nick: str
    login: str
    password: str
    email: EmailStr
    money: int
    north: Dict[str, int]
    lim: Dict[str, int]
    bp_level: int
    bp_exp: int
    days: List[DayRecord]
    reg_date: str | None = None

