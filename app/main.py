from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models, schemas
from app.database import engine, SessionLocal
from .routers import post, user, auth, vote
from . database import get_db
from .config import settings
#
# models.Base.metadata.drop_all(bind=engine)  # Drops all tables defined in models
# models.Base.metadata.create_all(bind=engine)  # Recreates all tables

app = FastAPI()
origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

app.include_router(vote.router)