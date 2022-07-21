from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, Float
from sqlalchemy.ext.indexable import index_property
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    prefs = Column(JSON, default={'last_sync_all': 0})

    last_sync_all = index_property('prefs', 'last_sync_all')

    # children
    checklist = relationship("ChecklistEntry", back_populates="user", lazy='selectin')


class Contest(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    month = Column(String)
    division = Column(String)

    # children
    problems = relationship("Problem", back_populates="contest", lazy='selectin')

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    # parent
    contest_id = Column(Integer, ForeignKey("contests.id"))
    contest = relationship("Contest", back_populates="problems", lazy='selectin')

    # chilren
    entries = relationship("ChecklistEntry", back_populates="problem", lazy='selectin')

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class ChecklistEntry(Base):
    __tablename__ = "checklist_entries"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Integer)

    # parent
    problem_id = Column(Integer, ForeignKey("problems.id"))
    problem = relationship("Problem", back_populates="entries", lazy='selectin')
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="checklist", lazy='selectin')

    # children
    cases = relationship("ChecklistEntryCase", back_populates="entry", lazy='selectin')

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class ChecklistEntryCase(Base):
    __tablename__ = "checklist_entry_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(Integer)
    is_correct = Column(Boolean)
    symbol = Column(String)
    memory_used = Column(String)
    time_taken = Column(String)

    # parent
    entry_id = Column(Integer, ForeignKey("checklist_entries.id"))
    entry = relationship("ChecklistEntry", back_populates="cases", lazy='selectin')

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
