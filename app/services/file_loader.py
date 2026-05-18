import hashlib
import os
from fastapi import UploadFile

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename or "")[1].lower()


def validate_supported_file(filename: str) -> None:
    ext = get_file_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type. Allowed: PDF, DOCX, TXT, MD")


def calculate_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


async def save_uploaded_file(file: UploadFile, upload_dir: str = "uploads") -> str:
    """Backward-compatible helper used by older code paths."""
    validate_supported_file(file.filename)
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return file_path


def save_uploaded_file_content(
    filename: str,
    content: bytes,
    upload_dir: str = "uploads",
) -> str:
    validate_supported_file(filename)
    os.makedirs(upload_dir, exist_ok=True)

    file_hash = calculate_sha256(content)
    ext = get_file_extension(filename)

    # Hash-based filename avoids overwriting files with the same original name.
    file_path = os.path.join(upload_dir, f"{file_hash}{ext}")

    if not os.path.exists(file_path):
        with open(file_path, "wb") as buffer:
            buffer.write(content)

    return file_path


def load_file_as_documents(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
        return loader.load()

    if ext == ".docx":
        loader = Docx2txtLoader(file_path)
        return loader.load()

    if ext in [".txt", ".md"]:
        loader = TextLoader(file_path, encoding="utf-8")
        return loader.load()

    raise ValueError("Unsupported file type. Allowed: PDF, DOCX, TXT, MD")
