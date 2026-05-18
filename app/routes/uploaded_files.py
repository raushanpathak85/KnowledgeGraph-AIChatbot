from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.file_loader import (
    calculate_sha256,
    save_uploaded_file_content,
    load_file_as_documents,
    validate_supported_file,
)
from app.services.ingestion_service import ingest_documents
from app.services.graph_service import (
    uploaded_file_exists,
    register_ingested_file,
    get_uploaded_file_graph_cypher,
)
from app.services.neo4j_graph_visualization_service import generate_neo4j_graph_html


router = APIRouter(prefix="/uploaded-files", tags=["Uploaded Files"])


@router.post("/ingest")
async def ingest_uploaded_file(file: UploadFile = File(...)):
    try:
        validate_supported_file(file.filename)

        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        file_hash = calculate_sha256(file_content)

        existing_file = uploaded_file_exists(file_hash)
        if existing_file:
            graph_result = generate_neo4j_graph_html(
                cypher=get_uploaded_file_graph_cypher(),
                params={"file_hash": file_hash},
            )

            return {
                "status": "duplicate_skipped",
                "message": "This file already exists. Pinecone and Neo4j ingestion skipped.",
                "filename": file.filename,
                "file_hash": file_hash,
                "existing_file": existing_file,
                "graph": graph_result,
            }

        file_path = save_uploaded_file_content(
            filename=file.filename,
            content=file_content,
        )

        documents = load_file_as_documents(file_path)

        result = ingest_documents(
            documents=documents,
            source_type="uploaded_file",
            title=file.filename,
            source_url=None,
            document_id=file_hash,
            metadata={
                "filename": file.filename,
                "content_type": file.content_type or "",
                "file_hash": file_hash,
                "file_path": file_path,
            },
        )

        register_ingested_file(
            file_hash=file_hash,
            title=file.filename,
            source_type="uploaded_file",
            content_type=file.content_type or "",
            file_path=file_path,
        )

        graph_result = generate_neo4j_graph_html(
            cypher=get_uploaded_file_graph_cypher(),
            params={"file_hash": file_hash},
        )

        return {
            **result,
            "message": "File ingested successfully into Pinecone and Neo4j. Knowledge graph generated.",
            "filename": file.filename,
            "graph": graph_result,
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
