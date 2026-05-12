import os
from fastapi import UploadFile

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader


async def save_uploaded_file(file: UploadFile, upload_dir: str = "uploads") -> str:
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
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