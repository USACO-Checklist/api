from pydantic import BaseModel
from typing import Optional


class ChecklistEntryCaseBase(BaseModel):
    case_number: int
    is_correct: bool
    symbol: str
    memory_used: str
    time_taken: str


class ChecklistEntryCaseUpdate(ChecklistEntryCaseBase):
    entry_id: int


class ChecklistEntryCaseCreate(ChecklistEntryCaseBase):
    pass


class ChecklistEntryCase(ChecklistEntryCaseBase):
    id: int
    entry_id: int

    class Config:
        orm_mode = True


class ChecklistEntryBase(BaseModel):
    status: int


class ChecklistEntryUpdate(ChecklistEntryBase):
    problem_id: int


class ChecklistEntryCreate(ChecklistEntryBase):
    pass


class ChecklistEntry(ChecklistEntryBase):
    id: int
    problem_id: int
    user_id: int
    cases: list[ChecklistEntryCase] = []

    class Config:
        orm_mode = True


class ProblemBase(BaseModel):
    id: int
    name: str


class ProblemCreate(ProblemBase):
    pass


class Problem(ProblemBase):
    contest_id: int
    entries: list[ChecklistEntry] = []

    class Config:
        orm_mode = True


class ContestBase(BaseModel):
    year: int
    month: str
    division: str


class ContestCreate(ContestBase):
    pass


class Contest(ContestBase):
    id: int
    problems: list[Problem] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserUpdate(UserBase):
    old_password: str
    new_password: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    uuid: str
    last_sync_all: int
    checklist: list[ChecklistEntry] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    iss: str  # issuer
    sub: str  # subject (username?), must be unique
    iat: int  # utc unix time
    exp: int  # expires at utc unix time
    jti: str  # token identifier
    scopes: list[str] = []  # permissions


class TokenData(BaseModel):
    username: Optional[str]
    scopes: list[str] = []
