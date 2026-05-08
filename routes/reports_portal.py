from fastapi import APIRouter, HTTPException

from app.schemas.report_schema import ReportIngestRequest
from app.services.ingestion_service import ingest_report_content


router = APIRouter(prefix="/reports-portal", tags=["Reports Portal"])


@router.post("/ingest")
def ingest_report(request: ReportIngestRequest):
    try:
        metadata = request.metadata or {}

        if request.author:
            metadata["author"] = request.author

        if request.sector:
            metadata["sector"] = request.sector

        if request.published_date:
            metadata["published_date"] = request.published_date

        result = ingest_report_content(
            title=request.title,
            content=request.content,
            source_url=request.source_url,
            metadata=metadata,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))