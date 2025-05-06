from pathlib import Path
from unidecode import unidecode
import PyPDF2

def load_pdf_text(path: Path) -> str:
    reader = PyPDF2.PdfReader(str(path))
    return "\n".join([unidecode(p.extract_text()) or "" for p in reader.pages])
