import time
import re
from typing import List
from sqlalchemy.orm import Session
from app.models import PDF
from app.utils import extract_name, extract_email
from app.logger import logger
from concurrent.futures import ProcessPoolExecutor
import asyncio
from multiprocessing import cpu_count
import fitz  # PyMuPDF

def read_pdf_text(filepath):
    """
    Read PDF text using PyMuPDF (fitz) for faster processing
    """
    text = ""
    try:
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        logger.error(f"Error reading PDF {filepath}: {e}")
        return ""

def process_single_pdf(pdf_data):
    """
    Process a single PDF to extract skills and details
    """
    try:
        pdf, skills = pdf_data
        logger.info(f"Starting to process PDF: {pdf.filename}")
        
        # Time the PDF reading operation
        read_start = time.time()
        text = read_pdf_text(pdf.filepath)
        read_time = round(time.time() - read_start, 2)
        logger.info(f"PDF read time for {pdf.filename}: {read_time} seconds")
        
        if not text:
            logger.warning(f"No text extracted from PDF: {pdf.filename}")
            return None
            
        # Time the skill matching operation
        match_start = time.time()
        matched_skills = [skill for skill in skills if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE)]
        match_time = round(time.time() - match_start, 2)
        logger.info(f"Skill matching time for {pdf.filename}: {match_time} seconds")
        
        if matched_skills:
            # Time the name and email extraction
            extract_start = time.time()
            name = extract_name(text)
            email = extract_email(text)
            extract_time = round(time.time() - extract_start, 2)
            logger.info(f"Name/Email extraction time for {pdf.filename}: {extract_time} seconds")
            
            total_time = round(read_time + match_time + extract_time, 2)
            logger.info(f"Total processing time for {pdf.filename}: {total_time} seconds")
            
            return {
                "name": name,
                "email": email,
                "pdf_id": pdf.id,
                "matched_skills": matched_skills,
                "timing": {
                    "read_time": read_time,
                    "match_time": match_time,
                    "extract_time": extract_time,
                    "total_time": total_time
                }
            }
        return None
    except Exception as e:
        logger.error(f"Error processing PDF {pdf.filename}: {e}")
        return None

def process_batch(batch_data):
    """
    Process a batch of PDFs and return list of results
    """
    results = []
    for pdf_data in batch_data:
        result = process_single_pdf(pdf_data)
        if result:
            results.append(result)
    return results

async def process_in_waves(executor, loop, batches, wave_size=10):
    """
    Process batches in waves to avoid overloading the event loop
    """
    results = []
    for i in range(0, len(batches), wave_size):
        wave = batches[i:i+wave_size]
        tasks = [loop.run_in_executor(executor, process_batch, b) for b in wave]
        res = await asyncio.gather(*tasks)
        results.extend(res)
        await asyncio.sleep(0)  # Yield control
    return results

async def search_skills_multiprocessing(skills: List[str], db: Session):
    start_time = time.time()
    logger.info(f"Starting batch multiprocessing skill search for skills: {skills}")
    
    pdfs = db.query(PDF).filter(PDF.is_deleted == False).all()
    logger.info(f"Found {len(pdfs)} PDFs to search through")
    
    pdf_data = [(pdf, skills) for pdf in pdfs]
    
    # Calculate optimal number of workers and batch size
    max_workers = min(4, cpu_count())
    batch_size = 5  # Changed to 5 as requested
    
    # Create batches
    batches = []
    for i in range(0, len(pdf_data), batch_size):
        batch = pdf_data[i:i + batch_size]
        batches.append(batch)
    
    logger.info(f"Created {len(batches)} batches with {batch_size} PDFs per batch")
    
    # Process batches in waves
    loop = asyncio.get_running_loop()
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        batch_results = await process_in_waves(executor, loop, batches)
    
    # Flatten results from all batches
    valid_results = [item for batch in batch_results for item in batch]
    
    time_taken = round(time.time() - start_time, 2)
    logger.info(f"Batch processing completed. {len(valid_results)} matches found in {time_taken} seconds.")
    
    # Calculate average read time
    read_times = [r.get('read_time', 0) for r in valid_results]
    avg_read_time = round(sum(read_times) / len(read_times) if read_times else 0, 2)
    
    return {
        "results": valid_results,
        "time_taken_seconds": time_taken,
        "total_pdfs_processed": len(pdfs),
        "number_of_batches": len(batches),
        "average_pdf_read_time": avg_read_time
    } 