from fastapi import FastAPI

from app.routes.uploaded_files import router as uploaded_files_router
from app.routes.reports_portal import router as reports_portal_router
from app.routes.query import router as query_router
from app.services.graph_service import create_graph_constraints


app = FastAPI(
    title="LangChain KG-RAG Backend",
    description="LangChain based KG-RAG using Pinecone, Neo4j, Claude and FastAPI",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    create_graph_constraints()


app.include_router(uploaded_files_router)
app.include_router(reports_portal_router)
app.include_router(query_router)


@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "RAG LangChain KG-RAG Backend",
    }