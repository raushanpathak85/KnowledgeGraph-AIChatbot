from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.file_loader import save_uploaded_file, load_file_as_documents
from app.services.ingestion_service import ingest_documents


router = APIRouter(prefix="/uploaded-files", tags=["Uploaded Files"])


@router.post("/ingest")
async def ingest_uploaded_file(file: UploadFile = File(...)):
    try:
        file_path = await save_uploaded_file(file)
        documents = load_file_as_documents(file_path)

        result = ingest_documents(
            documents=documents,
            source_type="uploaded_file",
            title=file.filename,
            source_url=None,
            metadata={
                "filename": file.filename,
                "content_type": file.content_type or "",
            },
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))