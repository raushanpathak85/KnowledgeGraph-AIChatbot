from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.services.langchain_clients import vector_store


def split_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )

    return splitter.split_documents(documents)


def store_documents_in_pinecone(documents: List[Document]) -> List[str]:
    ids = vector_store.add_documents(documents)
    return ids


def similarity_search(question: str, top_k: int = 5) -> List[Document]:
    return vector_store.similarity_search(
        query=question,
        k=top_k,
    )