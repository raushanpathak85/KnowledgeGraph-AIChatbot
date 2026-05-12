from pydantic import BaseModel


class GraphVisualizationRequest(BaseModel):
    text: str