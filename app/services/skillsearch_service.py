import time
import re
from typing import List
from sqlalchemy.orm import Session
from app.models import PDF
from app.utils import read_pdf_text, extract_name, extract_email
from app.logger import logger

async def search_skills(skills: List[str], db: Session):
    start_time = time.time()
    logger.info(f"Starting skill search for skills: {skills}")
    results = []

    pdfs = db.query(PDF).filter(PDF.is_deleted == False).all()
    logger.info(f"Found {len(pdfs)} PDFs to search through")

    for pdf in pdfs:
        try:
            logger.info(f"Processing PDF: {pdf.filename}")
            text = read_pdf_text(pdf.filepath)
            if not text:
                logger.warning(f"No text extracted from PDF: {pdf.filename}")
                continue

            matched_skills = [skill for skill in skills if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE)]
            logger.info(f"Found {len(matched_skills)} matching skills in {pdf.filename}: {matched_skills}")
            
            if matched_skills:
                name = extract_name(text)
                email = extract_email(text)
                logger.info(f"Extracted details from {pdf.filename} - Name: {name}, Email: {email}")
                
                results.append({
                    "name": name,
                    "email": email,
                    "pdf_id": pdf.id,
                    "matched_skills": matched_skills
                })
        except Exception as e:
            logger.error(f"Error processing PDF {pdf.filename}: {str(e)}")
            continue

    end_time = time.time()
    time_taken = round(end_time - start_time, 2)
    logger.info(f"Skill search completed. Found {len(results)} matches. Time taken: {time_taken} seconds")
    return {
        "results": results,
        "time_taken_seconds": time_taken
    } 