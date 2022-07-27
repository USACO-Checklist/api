import time

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from website.routers.views import views
from website.routers.auth import auth
from website.routers.problems import problems

app = FastAPI()

# app.mount("/static", StaticFiles(directory="website/static"), name="static")

origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:4000",
    "http://usaco.raybb.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(views)
app.include_router(auth, tags=["auth"])
app.include_router(problems, tags=["problems"])
