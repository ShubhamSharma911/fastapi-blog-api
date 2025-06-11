from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, oauth2
from app.database import get_db
from app.services import multiple_pdfs_service, skillsearch_service, skillsearch_multiprocessing_service
from app.logger import logger

router = APIRouter(
    prefix="/api/pdfs",
    tags=["PDFs"]
)

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Upload a single PDF file
    """
    try:
        pdf = await multiple_pdfs_service.upload_pdf(file, db)
        return {
            "message": "PDF uploaded successfully",
            "pdf_id": pdf.id,
            "filename": pdf.filename
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-multiple")
async def upload_multiple_pdfs(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Upload multiple PDF files
    """
    try:
        pdfs = await multiple_pdfs_service.upload_multiple_pdfs(files, db)
        return {
            "message": f"Successfully uploaded {len(pdfs)} PDFs",
            "pdfs": [
                {
                    "pdf_id": pdf.id,
                    "filename": pdf.filename
                } for pdf in pdfs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pdf_id}")
async def get_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Get a specific PDF by ID
    """
    pdf = multiple_pdfs_service.get_pdf_by_id(pdf_id, db)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    return pdf

@router.get("/")
async def get_all_pdfs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Get all PDFs with pagination
    """
    pdfs = multiple_pdfs_service.get_all_pdfs(db, skip, limit)
    return pdfs


@router.post("/search_skills", status_code=status.HTTP_200_OK)
async def search_skills(
    skills: list[str] = Query(..., description="List of skills to search for"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Search resumes for matching skills
    """
    logger.info(f"Received skill search request for skills: {skills}")
    try:
        results = await skillsearch_service.search_skills(skills, db)
        logger.info(f"Skill search completed successfully. Found {len(results['results'])} matches")
        return results
    except Exception as e:
        logger.error(f"Error in skill search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{pdf_id}")
async def delete_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Soft delete a PDF
    """
    success = multiple_pdfs_service.soft_delete_pdf(pdf_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="PDF not found")
    return {"message": "PDF deleted successfully"}

@router.post("/match-skills")
async def match_skills(
    skills: List[str],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Match PDFs based on skills
    """
    try:
        results = await multiple_pdfs_service.match_skills(skills, db)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match_skills_multiprocessing", status_code=status.HTTP_200_OK)
async def match_skills_multiprocessing(
    skills: list[str] = Query(..., description="List of skills to search for"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Search resumes for matching skills using multiprocessing for faster results
    """
    logger.info(f"Received multiprocessing skill search request for skills: {skills}")
    try:
        results = await skillsearch_multiprocessing_service.search_skills_multiprocessing(skills, db)
        logger.info(f"Multiprocessing skill search completed successfully. Found {len(results['results'])} matches")
        return results
    except Exception as e:
        logger.error(f"Error in multiprocessing skill search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))