import time
import re
from typing import List
from sqlalchemy.orm import Session
from app.models import PDF
from app.utils import read_pdf_text, extract_name, extract_email
from app.logger import logger
from multiprocessing import Pool, cpu_count

def process_single_pdf(pdf_data):
    """
    Process a single PDF to extract skills and details
    """
    try:
        pdf, skills = pdf_data
        logger.info(f"Processing PDF: {pdf.filename}")
        
        text = read_pdf_text(pdf.filepath)
        if not text:
            logger.warning(f"No text extracted from PDF: {pdf.filename}")
            return None

        matched_skills = [skill for skill in skills if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE)]
        logger.info(f"Found {len(matched_skills)} matching skills in {pdf.filename}: {matched_skills}")
        
        if matched_skills:
            name = extract_name(text)
            email = extract_email(text)
            logger.info(f"Extracted details from {pdf.filename} - Name: {name}, Email: {email}")
            
            return {
                "name": name,
                "email": email,
                "pdf_id": pdf.id,
                "matched_skills": matched_skills
            }
    except Exception as e:
        logger.error(f"Error processing PDF {pdf.filename}: {str(e)}")
        return None

async def search_skills_multiprocessing(skills: List[str], db: Session):
    start_time = time.time()
    logger.info(f"Starting multiprocessing skill search for skills: {skills}")
    
    # Get all PDFs
    pdfs = db.query(PDF).filter(PDF.is_deleted == False).all()
    logger.info(f"Found {len(pdfs)} PDFs to search through")
    
    # Prepare data for multiprocessing
    # below will create a list of tuples, each containing a pdf and the list of skills
    # this will be used to process the pdfs in parallel
    pdf_data = [(pdf, skills) for pdf in pdfs]
    
    # Use multiprocessing to process PDFs in parallel
    # cpu_count() will return the number of CPUs in the system
    # processes=cpu_count() will use all the CPUs in the system
    # pool.map will process the pdf_data in parallel
    # process_single_pdf will be called for each pdf in the pdf_data
    # process_single_pdf will return a dictionary containing the name, email, pdf_id, and matched_skills
    # the results will be a list of dictionaries
    # the valid_results will be a list of dictionaries that are not None
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(process_single_pdf, pdf_data)
    
    # Filter out None results and get valid matches
    valid_results = [r for r in results if r is not None]
    
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)
    logger.info(f"Multiprocessing skill search completed. Found {len(valid_results)} matches. Time taken: {time_taken} seconds")
    
    return {
        "results": valid_results,
        "time_taken_seconds": time_taken,
        "total_pdfs_processed": len(pdfs)
    } 