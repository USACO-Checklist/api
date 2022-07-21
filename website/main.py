import time

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from website.routers.views import views
from website.routers.auth import auth
from website.routers.problems import problems

app = FastAPI()

app.mount("/static", StaticFiles(directory="website/static"), name="static")

app.include_router(views)
app.include_router(auth, tags=["auth"])
app.include_router(problems, tags=["problems"])
