from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.services.langchain_clients import llm
from app.services.vector_service import similarity_search
from app.services.graph_service import get_graph_context


ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """
You are RAG, an analyst research assistant.

Use both:
1. Vector context from reports/uploaded files
2. Knowledge graph context from Neo4j

Question:
{question}

Knowledge Graph Context:
{graph_context}

Vector Context:
{vector_context}

Answer in a clear analyst style.

Include:
- Direct answer
- Supporting evidence
- Graph-based relationships
- Gaps or uncertainty
"""
)


def build_vector_context(docs):
    context_parts = []

    for doc in docs:
        title = doc.metadata.get("title", "Unknown")
        source_type = doc.metadata.get("source_type", "Unknown")
        source_url = doc.metadata.get("source_url", "")

        context_parts.append(
            f"""
Source Title: {title}
Source Type: {source_type}
Source URL: {source_url}

Content:
{doc.page_content}
"""
        )

    return "\n\n---\n\n".join(context_parts)


def build_citations(docs):
    citations = []

    for doc in docs:
        citations.append(
            {
                "title": doc.metadata.get("title"),
                "source_type": doc.metadata.get("source_type"),
                "source_url": doc.metadata.get("source_url"),
                "page": doc.metadata.get("page"),
                "document_id": doc.metadata.get("document_id"),
            }
        )

    return citations


def hybrid_kg_rag_answer(question: str, top_k: int = 5):
    docs = similarity_search(question=question, top_k=top_k)

    vector_context = build_vector_context(docs)
    graph_context = get_graph_context(question)

    chain = ANSWER_PROMPT | llm | StrOutputParser()

    answer = chain.invoke(
        {
            "question": question,
            "vector_context": vector_context,
            "graph_context": graph_context,
        }
    )

    return {
        "question": question,
        "answer": answer,
        "graph_context": graph_context,
        "citations": build_citations(docs),
    }