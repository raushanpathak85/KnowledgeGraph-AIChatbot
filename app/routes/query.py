from fastapi import APIRouter, HTTPException

from app.schemas.query_schema import QueryRequest
from app.services.rag_service import hybrid_kg_rag_answer


router = APIRouter(prefix="/query", tags=["Hybrid KG RAG"])


@router.post("/ask")
def ask_question(request: QueryRequest):
    try:
        return hybrid_kg_rag_answer(
            question=request.question,
            top_k=request.top_k,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))