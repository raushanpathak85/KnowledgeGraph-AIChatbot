from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.neo4j_graph_visualization_service import generate_neo4j_graph_html
from app.services.prompt_to_cypher_service import prompt_to_cypher


router = APIRouter(
    prefix="/neo4j-graph",
    tags=["Neo4j Graph Visualization"],
)


class Neo4jPromptGraphRequest(BaseModel):
    prompt: str


@router.post("/visualize-from-prompt")
def visualize_from_prompt(request: Neo4jPromptGraphRequest):
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt is required")

        cypher = prompt_to_cypher(request.prompt)

        result = generate_neo4j_graph_html(cypher)

        return {
            "status": "success",
            "message": "Neo4j graph visualization generated from prompt",
            "prompt": request.prompt,
            "generated_cypher": cypher,
            **result,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))