from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import os
from .logger import logger
from .routers import post, user, auth, vote, resume, pdfs
from app.middleware.logging import LoggingMiddleware

app = FastAPI()

# Register middleware
app.add_middleware(LoggingMiddleware)


origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/resumes", StaticFiles(directory="resumes"), name="resumes")
app.mount("/pdfs", StaticFiles(directory="pdfs"), name="pdfs")

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

app.include_router(vote.router)

app.include_router(resume.router)
app.include_router(pdfs.router)

@app.get("/")
def root(request: Request):
    logger.info(f"Root directory accessed: {request.method} {request.url.path}")
    return {"message":"Hello, World!"}