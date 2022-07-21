from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from website.internal import models, schemas
from website.routers.auth import get_current_user_optional


async def get_user(
        db: AsyncSession,
        id: int
) -> models.User:
    result = await db.execute(select(models.User).filter(models.User.id == id))
    return result.scalars().first()


async def get_user_by_uuid(
        db: AsyncSession,
        uuid: str
) -> models.User:
    result = await db.execute(select(models.User).filter(models.User.uuid == uuid))
    return result.scalars().first()


async def get_user_by_username(
        db: AsyncSession,
        username: str
) -> models.User:
    result = await db.execute(select(models.User).filter(models.User.username == username))
    return result.scalars().first()


async def get_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
) -> list[models.User]:
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()


async def create_user(
        db: AsyncSession,
        user: schemas.UserCreate,
        user_uuid: str
) -> models.User:
    new_user = models.User(uuid=user_uuid, username=user.username, hashed_password=user.password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(
        db: AsyncSession,
        user: schemas.UserUpdate,
) -> models.User:
    current_user = await get_user_by_username(db, user.username)
    current_user.hashed_password = user.new_password
    await db.commit()
    await db.refresh(current_user)
    return current_user


async def get_contest(
        db: AsyncSession,
        id: int
) -> models.Contest:
    result = await db.execute(select(models.Contest).filter(models.Contest.id == id))
    return result.scalars().first()


async def get_contest_by_info(
        db: AsyncSession,
        year: int,
        month: str,
        division: str
) -> models.Contest:
    result = await db.execute(select(models.Contest).filter(models.Contest.year == year, models.Contest.month == month, models.Contest.division == division))
    return result.scalars().first()


async def get_contests(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 1000
) -> list[models.Contest]:
    result = await db.execute(select(models.Contest).offset(skip).limit(limit))
    return result.scalars().all()


async def create_contest(
        db: AsyncSession,
        contest: schemas.ContestCreate
) -> models.Contest:
    new_contest = models.Contest(year=contest.year, month=contest.month, division=contest.division)
    db.add(new_contest)
    await db.commit()
    await db.refresh(new_contest)
    return new_contest


async def get_problem(
        db: AsyncSession,
        id: int
) -> models.Problem:
    result = await db.execute(select(models.Problem).filter(models.Problem.id == id))
    return result.scalars().first()


async def get_problems_by_contest(
        db: AsyncSession,
        contest_id: int
) -> list[models.Problem]:
    result = await db.execute(select(models.Problem).filter(models.Problem.contest_id == contest_id))
    return result.scalars().all()


async def get_problems(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 1000
) -> list[models.Problem]:
    result = await db.execute(select(models.Problem).offset(skip).limit(limit))
    return result.scalars().all()


async def create_problem(
        db: AsyncSession,
        problem: schemas.ProblemCreate,
        contest_id: int
) -> models.Problem:
    new_problem = models.Problem(id=problem.id, name=problem.name, contest_id=contest_id)
    db.add(new_problem)
    await db.commit()
    await db.refresh(new_problem)
    return new_problem


async def get_checklist_entry(
        db: AsyncSession,
        id: int
) -> models.ChecklistEntry:
    result = await db.execute(select(models.ChecklistEntry).filter(models.ChecklistEntry.id == id))
    return result.scalars().first()


async def get_checklist_of_user(
        db: AsyncSession,
        user_id: int
) -> list[models.ChecklistEntry]:
    result = await db.execute(select(models.ChecklistEntry).filter(models.ChecklistEntry.user_id == user_id))
    return result.scalars().all()


async def get_checklist_of_uuid(
        db: AsyncSession,
        uuid: str
) -> list[models.ChecklistEntry]:
    user_id = (await get_user_by_uuid(db, uuid)).id
    return await get_checklist_of_user(db, user_id)


async def get_checklist_entry_of_user_problem(
        db: AsyncSession,
        user_id: int,
        problem_id: int
) -> models.ChecklistEntry:
    result = await db.execute(select(models.ChecklistEntry).filter(models.ChecklistEntry.user_id == user_id, models.ChecklistEntry.problem_id == problem_id))
    return result.scalars().first()


async def get_checklist_entries_of_problem(
        db: AsyncSession,
        problem_id: int,
        skip: int = 0,
        limit: int = 100
) -> list[models.ChecklistEntry]:
    result = await db.execute(select(models.ChecklistEntry).filter(models.ChecklistEntry.problem_id == problem_id).offset(skip).limit(limit))
    return result.scalars().all()


async def get_checklist_entries(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
) -> list[models.ChecklistEntry]:
    result = await db.execute(select(models.ChecklistEntry).offset(skip).limit(limit))
    return result.scalars().all()


async def create_checklist_entry(
        db: AsyncSession,
        checklist_entry: schemas.ChecklistEntryCreate,
        user_id: int,
        problem_id: int
) -> models.ChecklistEntry:
    new_checklist_entry = models.ChecklistEntry(status=checklist_entry.status, user_id=user_id, problem_id=problem_id)
    db.add(new_checklist_entry)
    await db.commit()
    await db.refresh(new_checklist_entry)
    return new_checklist_entry


async def update_checklist_entry(
        db: AsyncSession,
        entry: schemas.ChecklistEntryUpdate,
        user_id: int
) -> models.ChecklistEntry:
    current_entry = await get_checklist_entry_of_user_problem(db, user_id, entry.problem_id)
    current_entry.status = entry.status
    await db.commit()
    await db.refresh(current_entry)
    return current_entry


async def get_checklist_entry_case(
        db: AsyncSession,
        id: int
) -> models.ChecklistEntryCase:
    result = await db.execute(select(models.ChecklistEntryCase).filter(models.ChecklistEntryCase.id == id))
    return result.scalars().first()


async def get_checklist_entry_cases_of_user(
        db: AsyncSession,
        user_id: int
) -> list[models.ChecklistEntryCase]:
    checklist_entry_cases = []
    for checklist_entry in await get_checklist_of_user(db, user_id):
        for checklist_entry_case in await get_checklist_entry_cases_of_checklist_entry(db, checklist_entry.id):
            checklist_entry_cases.append(checklist_entry_case)
    return checklist_entry_cases


async def get_checklist_entry_cases_of_uuid(
        db: AsyncSession,
        uuid: str
) -> list[models.ChecklistEntryCase]:
    user_id = (await get_user_by_uuid(db, uuid)).id
    return await get_checklist_entry_cases_of_user(db, user_id)


async def get_checklist_entry_case_of_checklist_entry_number(
        db: AsyncSession,
        entry_id: int,
        case_number: int
) -> models.ChecklistEntryCase:
    result = await db.execute(select(models.ChecklistEntryCase).filter(models.ChecklistEntryCase.entry_id == entry_id, models.ChecklistEntryCase.case_number == case_number))
    return result.scalars().first()


async def get_checklist_entry_cases_of_checklist_entry(
        db: AsyncSession,
        entry_id: int
) -> list[models.ChecklistEntryCase]:
    result = await db.execute(select(models.ChecklistEntryCase).filter(models.ChecklistEntryCase.entry_id == entry_id))
    return result.scalars().all()


async def get_checklist_entry_cases(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
) -> list[models.ChecklistEntryCase]:
    result = await db.execute(select(models.ChecklistEntryCase).offset(skip).limit(limit))
    return result.scalars().all()


async def create_checklist_entry_case(
        db: AsyncSession,
        checklist_entry_case: schemas.ChecklistEntryCaseCreate,
        entry_id: int
) -> models.ChecklistEntryCase:
    new_checklist_entry_case = models.ChecklistEntryCase(case_number=checklist_entry_case.case_number, is_correct=checklist_entry_case.is_correct, symbol=checklist_entry_case.symbol,
                                                         memory_used=checklist_entry_case.memory_used, time_taken=checklist_entry_case.time_taken, entry_id=entry_id)
    db.add(new_checklist_entry_case)
    await db.commit()
    await db.refresh(new_checklist_entry_case)
    return new_checklist_entry_case


async def update_checklist_entry_case(
        db: AsyncSession,
        updated_entry_case: schemas.ChecklistEntryCaseUpdate
) -> models.ChecklistEntryCase:
    current_entry_case = await get_checklist_entry_case_of_checklist_entry_number(db, updated_entry_case.entry_id, updated_entry_case.case_number)
    current_entry_case.symbol = updated_entry_case.symbol
    current_entry_case.is_correct = updated_entry_case.is_correct
    current_entry_case.memory_used = updated_entry_case.memory_used
    current_entry_case.time_taken = updated_entry_case.time_taken
    await db.commit()
    await db.refresh(current_entry_case)
    return current_entry_case
