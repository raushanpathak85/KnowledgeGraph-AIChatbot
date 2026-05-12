from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.staticfiles import StaticFiles
from app.routes.uploaded_files import router as uploaded_files_router
from app.routes.reports_portal import router as reports_portal_router
from app.routes.query import router as query_router
from app.services.graph_service import create_graph_constraints
from app.routes.graph_visualization import router as graph_visualization_router
from app.routes.neo4j_graph_visualization import router as neo4j_graph_visualization_router

app = FastAPI(
    title="LangChain KG-RAG Backend",
    description="LangChain based KG-RAG using Pinecone, Neo4j, Claude and FastAPI",
    version="1.0.0",
)

# CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    create_graph_constraints()


app.include_router(uploaded_files_router)
app.include_router(reports_portal_router)
app.include_router(query_router)

 
app.include_router(graph_visualization_router)
app.include_router(neo4j_graph_visualization_router)


@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "RAG LangChain KG-RAG Backend",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",   
        host="0.0.0.0",
        port=8000,
        reload=True
    )