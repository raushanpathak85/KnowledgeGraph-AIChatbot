from typing import List
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer

from app.services.langchain_clients import llm, graph


ALLOWED_NODES = [
    "Company",
    "Sector",
    "SubSector",
    "Analyst",
    "Report",
    "Topic",
    "Theme",
    "Region",
    "Client",
    "Event",
    "Product",
    "Person",
    "Metric",
    "Risk",
    "Opportunity",
    "Document",
]

ALLOWED_RELATIONSHIPS = [
    "MENTIONS",
    "BELONGS_TO",
    "COMPETES_WITH",
    "COVERS",
    "DISCUSSES",
    "RELATED_TO",
    "IMPACTS",
    "AUTHORED_BY",
    "ASKED_ABOUT",
    "HAS_RISK",
    "HAS_OPPORTUNITY",
    "LOCATED_IN",
    "PART_OF",
    "HAS_METRIC",
]


def create_graph_constraints():
    graph.query(
        """
        CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
        FOR (n:__Entity__)
        REQUIRE n.id IS UNIQUE
        """
    )


def store_documents_in_neo4j(documents: List[Document]):
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=ALLOWED_NODES,
        allowed_relationships=ALLOWED_RELATIONSHIPS,
        strict_mode=False,
    )

    graph_documents = llm_transformer.convert_to_graph_documents(documents)

    graph.add_graph_documents(
        graph_documents,
        baseEntityLabel=True,
        include_source=True,
    )

    return {
        "graph_documents_created": len(graph_documents)
    }


def get_graph_context(question: str) -> str:
    query = """
    MATCH (e:__Entity__)-[r]-(related)
    WHERE e.id IS NOT NULL
      AND toLower($question) CONTAINS toLower(toString(e.id))

    RETURN
        toString(e.id) AS entity,
        type(r) AS relationship,
        coalesce(toString(related.id), '') AS related_entity,
        labels(related) AS related_labels

    LIMIT 50
    """

    result = graph.query(query, params={"question": question})

    lines = []

    for row in result:
        entity = row.get("entity") or ""
        relationship = row.get("relationship") or ""
        related_entity = row.get("related_entity") or ""
        related_labels = row.get("related_labels") or []

        if related_entity:
            lines.append(
                f"{entity} -[{relationship}]- {related_entity} {related_labels}"
            )

    return "\n".join(lines)