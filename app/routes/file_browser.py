import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/files", tags=["File Browser"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GRAPHS_DIR = PROJECT_ROOT / "static" / "graphs"
UPLOADS_DIR = PROJECT_ROOT / "uploads"


class BrowserFile(BaseModel):
    filename: str
    file_type: str
    size_bytes: int
    created_at: str
    modified_at: str
    url: str


def _safe_list_files(directory: Path, url_prefix: str, allowed_extensions: set[str]) -> List[BrowserFile]:
    if not directory.exists():
        return []

    if not directory.is_dir():
        raise HTTPException(status_code=500, detail=f"Invalid directory: {directory}")

    files: List[BrowserFile] = []

    for path in directory.iterdir():
        if not path.is_file():
            continue

        if path.suffix.lower() not in allowed_extensions:
            continue

        stat = path.stat()
        mime_type, _ = mimetypes.guess_type(path.name)

        files.append(
            BrowserFile(
                filename=path.name,
                file_type=mime_type or "application/octet-stream",
                size_bytes=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
                modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                url=f"{url_prefix}/{path.name}",
            )
        )

    # Latest files first
    files.sort(key=lambda item: item.modified_at, reverse=True)
    return files


@router.get("/graphs", response_model=list[BrowserFile])
def list_generated_graphs():
    """List all generated graph HTML files from static/graphs."""
    return _safe_list_files(
        directory=GRAPHS_DIR,
        url_prefix="/static/graphs",
        allowed_extensions={".html", ".htm"},
    )


@router.get("/uploads", response_model=list[BrowserFile])
def list_uploaded_documents():
    """List all uploaded documents from uploads folder."""
    return _safe_list_files(
        directory=UPLOADS_DIR,
        url_prefix="/uploads",
        allowed_extensions={".pdf", ".docx", ".txt", ".md"},
    )
