# from email.feedparser import headerRE
from fastapi import Query
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks, Header
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import resume_service
from app.schemas import ResumeUploadResponse
from fastapi.params import Depends
from app import models, schemas
from app import oauth2  # For JWT dependency
router = APIRouter(prefix="/file",
                   tags=["Resumes"]
                   )


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user) ,background_tasks: BackgroundTasks = None):
    return await resume_service.upload_resume(user_id=current_user.id , file=file, db=db,background_tasks=background_tasks )


@router.get("/download")
def get_resume_url(db: Session = Depends(get_db),current_user:dict = Depends(oauth2.get_current_user)):
    resume = resume_service.get_resume_by_user(user_id=current_user.id, db=db)

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"url": f"/resumes/{resume.filename}"}

@router.get("/status")
def get_status(current_user: models.User = Depends(oauth2.get_current_user),
               db: Session = Depends(get_db)
               ):
    resume =  db.query(models.Resume).filter(models.Resume.user_id == current_user.id).first()
    return resume.status.value

@router.post("/upload-multiple", status_code=status.HTTP_201_CREATED)
async def upload_multiple_resumes(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    background_tasks: BackgroundTasks = None
):
    responses = []
    for file in files:
        response = await resume_service.upload_resume(
            user_id=current_user.id,
            file=file,
            db=db,
            background_tasks=background_tasks
        )
        responses.append(response)
    return responses




@router.post("/search-skills", status_code=status.HTTP_200_OK)
async def search_resumes_by_skills(
    skills: list[str] = Query(..., description="List of skills to search for"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    data = await resume_service.parse_resumes_without_multiprocessing(skills=skills, db=db)
    return data
