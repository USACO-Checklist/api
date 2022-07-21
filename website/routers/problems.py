import json
import time
from typing import Optional

from fastapi import APIRouter, Depends, Security, BackgroundTasks, Request, HTTPException, status, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session as Database
from sqlalchemy.ext.asyncio import AsyncSession

from website.internal.database import get_session, get_sync_session
from website.internal import models, schemas, crud
from website.internal.scripts import web_scrape_problem_cases, admin_web_scrape_problems
from website.routers.auth import get_current_user_optional, get_current_user_required

from requests import Session

problems = APIRouter()
templates = Jinja2Templates(directory="website/templates")

SYNC_ALL_DELAY = 300


@problems.get("/problems/sync-usaco")
async def sync_usaco_data(
        request: Request,
        current_user: schemas.User = Security(get_current_user_required, scopes=['me'])
):
    return templates.TemplateResponse("sync-usaco.html", {"request": request, "user": current_user})


async def login_to_usaco(
        s: Session,
        uname: str,
        password: str,
):
    post_url = 'http://www.usaco.org/current/tpcm/login-session.php'
    payload = {'uname': uname, 'password': password}
    r = s.post(post_url, data=payload)
    login_response = json.loads(r.text)
    if login_response["msg"] == "Incorrect password":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Incorrect USACO credentials",
        )


@problems.post('/admin/fetch-all-problems')
async def fetch_all_problems(
        tasks: BackgroundTasks,
        db: Database = Depends(get_sync_session),
        current_user: schemas.User = Security(get_current_user_required, scopes=['admin'])
):
    tasks.add_task(admin_web_scrape_problems, db)

    return {'status': 'fetching problems, please wait'}


@problems.put('/problems/update', response_model=schemas.ChecklistEntry)
async def update_problem_status(
        update_info: schemas.ChecklistEntryUpdate,
        db: AsyncSession = Depends(get_session),
        current_user: schemas.User = Security(get_current_user_required, scopes=['me'])
):
    # TODO: internal checks
    current_entry = await crud.get_checklist_entry_of_user_problem(db, current_user.id, update_info.problem_id)
    if not current_entry:
        entry = schemas.ChecklistEntryCreate(status=update_info.status)
        new_entry = await crud.create_checklist_entry(db, entry, current_user.id, update_info.problem_id)
        return new_entry
    else:
        updated_entry = await crud.update_checklist_entry(db, update_info, current_user.id)
        return updated_entry


@problems.post('/problems/fetch-all-cases/')
async def fetch_all_cases(
        tasks: BackgroundTasks,
        usaco_uname: str = Form(),
        usaco_password: str = Form(),
        db: Database = Depends(get_sync_session),
        current_user: schemas.User = Security(get_current_user_required, scopes=['me'])
):
    last_sync_time = current_user.last_sync_all
    curr_time = time.time()
    if curr_time - last_sync_time <= SYNC_ALL_DELAY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Next sync all available in {} seconds".format(SYNC_ALL_DELAY - int(curr_time - last_sync_time)),
        )
    current_user.last_sync_all = curr_time
    db.commit()

    s = Session()
    await login_to_usaco(s, usaco_uname, usaco_password)
    tasks.add_task(web_scrape_problem_cases, db, s, current_user.id)

    return {'status': 'fetching all problem cases, please wait'}


@problems.get('/problems/get-problem-info')
async def get_problem_info(
        db: AsyncSession = Depends(get_session)
):
    contests = []
    for contest in await crud.get_contests(db):
        contests.append(contest.as_dict())
    problems = []
    for problem in await crud.get_problems(db):
        problems.append(problem.as_dict())
    return {'contests': json.dumps(contests), 'problems': json.dumps(problems)}


@problems.get('/problems/get-checklist-info/{uuid}')
async def get_checklist_info(
        uuid: str,
        db: AsyncSession = Depends(get_session)
):
    entries = []
    for checklist_entry in await crud.get_checklist_of_uuid(db, uuid):
        entries.append(checklist_entry.as_dict())
    cases = []
    for checklist_entry_case in await crud.get_checklist_entry_cases_of_uuid(db, uuid):
        cases.append(checklist_entry_case.as_dict())
    return {'entries': json.dumps(entries), 'cases': json.dumps(cases)}


@problems.get('/problems', response_class=HTMLResponse)
async def view_other_problems(
        request: Request,
        uuid: Optional[str] = None,
        db: AsyncSession = Depends(get_session),
        current_user: schemas.User = Depends(get_current_user_optional)
):
    if uuid:
        list_author = await crud.get_user_by_uuid(db, uuid)
    else:
        list_author = current_user
    return templates.TemplateResponse("problems.html", {"request": request, "user": current_user, "list_author": list_author})
