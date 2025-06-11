import os
from datetime import datetime
from typing import List
from uuid import uuid4

import aiofiles
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.logger import logger
from app.models import PDF

UPLOAD_DIR = "pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_pdf_to_disk(file: UploadFile) -> tuple[str, str]:
    """
    Save an uploaded PDF file to disk with a unique filename
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4().hex}_{timestamp}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    logger.info(f"Saved PDF file: {file_path} to disk")
    return file_path, unique_filename

async def upload_pdf(file: UploadFile, db: Session) -> PDF:
    """
    Upload a single PDF file and create a record in the database
    """
    if not file.filename.endswith(".pdf"):
        logger.warning(f"Attempted to upload unsupported file format: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    logger.info(f"Uploading PDF file: {file.filename}")
    
    file_path, filename = await save_pdf_to_disk(file)
    
    # Create new PDF record
    new_pdf = PDF(
        filename=filename,
        filepath=file_path
    )
    
    db.add(new_pdf)
    db.commit()
    db.refresh(new_pdf)
    
    logger.info(f"Successfully saved PDF {filename} at {file_path}")
    return new_pdf

async def upload_multiple_pdfs(files: List[UploadFile], db: Session) -> List[PDF]:
    """
    Upload multiple PDF files and create records in the database
    """
    uploaded_pdfs = []
    
    for file in files:
        try:
            pdf = await upload_pdf(file, db)
            uploaded_pdfs.append(pdf)
        except Exception as e:
            logger.error(f"Error uploading PDF {file.filename}: {str(e)}")
            continue
    
    return uploaded_pdfs

def get_pdf_by_id(pdf_id: int, db: Session) -> PDF | None:
    """
    Fetch a PDF record by its ID
    """
    return db.query(PDF).filter(PDF.id == pdf_id).first()

def get_all_pdfs(db: Session, skip: int = 0, limit: int = 100) -> List[PDF]:
    """
    Fetch all PDF records with pagination
    """
    return db.query(PDF).filter(PDF.is_deleted == False).offset(skip).limit(limit).all()

def soft_delete_pdf(pdf_id: int, db: Session) -> bool:
    """
    Soft delete a PDF record by setting is_deleted to True
    """
    pdf = get_pdf_by_id(pdf_id, db)
    if not pdf:
        return False
    
    pdf.is_deleted = True
    db.commit()
    return True 