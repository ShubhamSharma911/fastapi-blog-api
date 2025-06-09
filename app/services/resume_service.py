import os
import time
from uuid import uuid4
from datetime import datetime

import aiofiles
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
import asyncio
from app import models
from app.logger import logger
from app.models import Resume, User
from app.schemas import ResumeUploadResponse
from app.status import Status
from app.utilsp.notifications import notify_all_services
from app.utils import extract_skills, read_pdf_text, extract_phone, extract_email, extract_name, extract_text

UPLOAD_DIR = "resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_file_to_disk(file: UploadFile) -> tuple[str, str]:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4().hex}_{timestamp}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    logger.info(f"Saved file: {file_path} to disk")
    return file_path, unique_filename

async def process_resume(user_id: int, file_path:str,file_name:str, db:Session, resume:Resume):

    await asyncio.sleep(10)

    # Check if resume already exists for user
    existing_resume = db.query(Resume).filter(Resume.user_id == user_id).first()
    if existing_resume:
        # Replace old resume file
        try:
            os.remove(existing_resume.filepath)
        except FileNotFoundError:
            pass
        existing_resume.filename = file_name
        existing_resume.filepath = file_path
        existing_resume.status = Status.SUCCESS.value
        db.commit()
        db.refresh(existing_resume)
        return existing_resume

    # Save new resume to DB
    new_resume = Resume(
        user_id=user_id,
        filename=file_name,
        filepath=file_path,
        status=Status.SUCCESS.value
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)


    logger.info(f"User {user_id} successfully saved {file_name} at {file_path}")
    return None

async def upload_resume(user_id: int, file: UploadFile, db: Session, background_tasks: BackgroundTasks,) -> ResumeUploadResponse:
    if not file.filename.endswith((".pdf", ".doc", ".docx")):
        logger.warning(f"User {user_id} attempted to upload unsupported file format: {file.filename}")
        raise HTTPException(status_code=400, detail="Unsupported file format")

    logger.info(f"User {user_id} uploading file: {file.filename}")
    resume = db.query(models.Resume).filter(models.Resume.user_id == user_id).first()

    resume.status = Status.PENDING.value
    db.commit()
    db.refresh(resume)

    file_path, filename = await save_file_to_disk(file)

    logger.info(f"Saved file to disk at {file_path}")

    background_tasks.add_task(
        process_resume, user_id=user_id, file_path=file_path, file_name=filename, db=db, resume=resume
    )

    logger.info(f"Background task added to process resume for user {user_id}")

    asyncio.create_task(notify_all_services(user_id, filename))

    return ResumeUploadResponse(
        message="Resume uploaded and will be processed shortly.",
        filename=filename,
        uploaded_at=datetime.utcnow()
    )


def get_resume_by_user(user_id: int, db: Session) -> Resume | None:
    """
    Fetch the resume record for a given user.
    """
    return db.query(Resume).filter(Resume.user_id == user_id).first()

import traceback


async def parse_resumes_without_multiprocessing(skills: list[str], db):
    start_time = time.time()
    results = []

    resumes = db.query(Resume).all()  # No need to await since it's now a sync function
    loop = asyncio.get_event_loop()


    for resume in resumes:
        # Step 1: Read text from PDF asynchronously
        text = read_pdf_text(resume.filepath)
        if not text:
            continue

        # Step 2: Extract skills
        matched_skills =  await loop.run_in_executor(None, read_pdf_text, resume.filepath)

        # Step 3: If skills found, extract details
        if matched_skills:
            name = extract_name(text)
            email = extract_email(text)
            phone = extract_phone(text)
            user = db.query(User).filter(User.id == resume.user_id).first()

            results.append({
                "user_id": resume.user_id,
                "username": user.email if user else None,
                "name": name,
                "email": email,
                "phone": phone,
                "skills": matched_skills
            })

    end_time = time.time()
    return {
        "results": results,
        "time_taken_seconds": round(end_time - start_time, 2)
    }

