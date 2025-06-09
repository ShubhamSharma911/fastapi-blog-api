from passlib.context import CryptContext
import re
from pdfminer.high_level import extract_text



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)




def extract_email(text: str) -> str:
    match = re.search(r'[\w.-]+@[\w.-]+', text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> str:
    match = re.search(r'\b\d{10}\b', text)  # basic 10-digit phone
    return match.group(0) if match else ""

def extract_name(text: str) -> str:
    # Dummy logic for name — use more advanced NLP later
    lines = text.strip().split('\n')
    return lines[0] if lines else ""

async def extract_skills(text: str, required_skills: list[str]) -> list[str]:
    found = []
    lower_text = text.lower()
    for skill in required_skills:
        if skill.lower() in lower_text:
            found.append(skill)


    return found

def read_pdf_text(file_path: str) -> str:
    try:
        return extract_text(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""