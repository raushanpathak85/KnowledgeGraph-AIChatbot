from fastapi import APIRouter, HTTPException, UploadFile, File

from app.schemas.graph_visualization_schema import GraphVisualizationRequest
from app.services.graph_visualization_service import generate_knowledge_graph_html
from app.services.file_loader import save_uploaded_file, load_file_as_documents


router = APIRouter(
    prefix="/knowledge-graph",
    tags=["Knowledge Graph Visualization"],
)


@router.post("/generate")
async def generate_graph(request: GraphVisualizationRequest):
    try:
        result = await generate_knowledge_graph_html(request.text)

        if not result:
            raise HTTPException(status_code=400, detail="No graph generated")

        return {
            "status": "success",
            "message": "Knowledge graph generated successfully",
            **result,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-from-pdf")
async def generate_graph_from_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed",
            )

        file_path = await save_uploaded_file(file)
        documents = load_file_as_documents(file_path)

        text = "\n\n".join([doc.page_content for doc in documents])

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF",
            )

        result = await generate_knowledge_graph_html(text)

        if not result:
            raise HTTPException(
                status_code=400,
                detail="No graph generated from PDF",
            )

        return {
            "status": "success",
            "message": "Knowledge graph generated from PDF successfully",
            "filename": file.filename,
            "pages": len(documents),
            **result,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))