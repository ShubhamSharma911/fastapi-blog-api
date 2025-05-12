from fastapi import FastAPI
from . import models, schemas
from app.database import engine, SessionLocal
from .routers import post, user, auth
from . database import get_db

models.Base.metadata.drop_all(bind=engine)  # Drops all tables defined in models
models.Base.metadata.create_all(bind=engine)  # Recreates all tables

app = FastAPI()



app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)