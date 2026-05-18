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

    graph.query(
        """
        CREATE CONSTRAINT ingested_document_hash_unique IF NOT EXISTS
        FOR (d:IngestedDocument)
        REQUIRE d.file_hash IS UNIQUE
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

def uploaded_file_exists(file_hash: str) -> dict | None:
    result = graph.query(
        """
        MATCH (d:IngestedDocument {file_hash: $file_hash})
        RETURN d.file_hash AS file_hash,
               d.title AS title,
               d.source_type AS source_type,
               d.created_at AS created_at
        LIMIT 1
        """,
        params={"file_hash": file_hash},
    )
    return result[0] if result else None


def register_ingested_file(
    file_hash: str,
    title: str,
    source_type: str,
    content_type: str = "",
    file_path: str = "",
):
    params = {
        "file_hash": file_hash,
        "title": title,
        "source_type": source_type,
        "content_type": content_type,
        "file_path": file_path,
    }

    graph.query(
        """
        MERGE (d:IngestedDocument {file_hash: $file_hash})
        ON CREATE SET
            d.title = $title,
            d.source_type = $source_type,
            d.content_type = $content_type,
            d.file_path = $file_path,
            d.created_at = datetime()
        ON MATCH SET
            d.last_seen_at = datetime()
        RETURN d.file_hash AS file_hash
        """,
        params=params,
    )

    graph.query(
        """
        MATCH (d:IngestedDocument {file_hash: $file_hash})
        MATCH (src:Document)
        WHERE src.file_hash = $file_hash
           OR src.document_id = $file_hash
        MERGE (d)-[:HAS_CHUNK]->(src)
        """,
        params=params,
    )


def get_uploaded_file_graph_cypher() -> str:
    # LangChain creates (:Document) source nodes when include_source=True.
    # Each source node gets chunk metadata, including file_hash.
    return """
    CALL {
        MATCH (uploaded:IngestedDocument {file_hash: $file_hash})-[r]-(doc:Document)
        RETURN uploaded AS s, r, doc AS t

        UNION

        MATCH (doc:Document)-[r]-(entity)
        WHERE doc.file_hash = $file_hash
           OR doc.document_id = $file_hash
        RETURN doc AS s, r, entity AS t

        UNION

        MATCH (doc:Document)-[]-(entity)-[r]-(related)
        WHERE doc.file_hash = $file_hash
           OR doc.document_id = $file_hash
        RETURN entity AS s, r, related AS t
    }
    RETURN s, r, t
    LIMIT 100
    """
