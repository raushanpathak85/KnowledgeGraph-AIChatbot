import uuid
from typing import List, Dict, Any

from langchain_core.documents import Document

from app.services.vector_service import split_documents, store_documents_in_pinecone
from app.services.graph_service import store_documents_in_neo4j


def enrich_documents_metadata(
    documents: List[Document],
    source_type: str,
    title: str,
    source_url: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> List[Document]:
    document_id = str(uuid.uuid4())
    metadata = metadata or {}

    enriched_docs = []

    for doc in documents:
        doc.metadata = {
            **doc.metadata,
            **metadata,
            "document_id": document_id,
            "title": title,
            "source_type": source_type,
            "source_url": source_url or "",
        }

        enriched_docs.append(doc)

    return enriched_docs


def ingest_documents(
    documents: List[Document],
    source_type: str,
    title: str,
    source_url: str | None = None,
    metadata: Dict[str, Any] | None = None,
):
    enriched_docs = enrich_documents_metadata(
        documents=documents,
        source_type=source_type,
        title=title,
        source_url=source_url,
        metadata=metadata,
    )

    chunks = split_documents(enriched_docs)

    vector_ids = store_documents_in_pinecone(chunks)

    graph_result = store_documents_in_neo4j(chunks[:5])

    return {
        "status": "ingested",
        "title": title,
        "source_type": source_type,
        "chunks_created": len(chunks),
        "pinecone_vectors_created": len(vector_ids),
        "neo4j_result": graph_result,
    }


def ingest_report_content(
    title: str,
    content: str,
    source_url: str | None = None,
    metadata: Dict[str, Any] | None = None,
):
    document = Document(
        page_content=content,
        metadata={
            "title": title,
            "source_url": source_url or "",
        },
    )

    return ingest_documents(
        documents=[document],
        source_type="reports_portal",
        title=title,
        source_url=source_url,
        metadata=metadata,
    )