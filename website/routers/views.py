from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Request, Depends, Security, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession

from website.internal import models, schemas, crud
from website.routers.auth import get_current_user_optional
from website.internal.database import get_session

views = APIRouter()
templates = Jinja2Templates(directory="website/templates")


async def do_something(db: AsyncSession):
    users = await crud.get_users(db)
    for user in users:
        print(user.username)

# @views.get('/', response_class=HTMLResponse)
# async def home(
#         request: Request,
#         current_user: Optional[schemas.User] = Depends(get_current_user_optional)
# ):
#     return templates.TemplateResponse("home.html", {"request": request, "user": current_user})
