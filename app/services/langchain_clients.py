from pinecone import Pinecone, ServerlessSpec

from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jGraph
from langchain_pinecone import PineconeVectorStore

from app.config import settings


llm = ChatAnthropic(
    model=settings.LLM_MODEL,
    temperature=0,
    anthropic_api_key=settings.ANTHROPIC_API_KEY,
)

embeddings = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL
)


pc = Pinecone(api_key=settings.PINECONE_API_KEY)


def get_or_create_pinecone_index():
    existing_indexes = [index.name for index in pc.list_indexes()]

    if settings.PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.PINECONE_CLOUD,
                region=settings.PINECONE_REGION,
            ),
        )

    return pc.Index(settings.PINECONE_INDEX_NAME)


pinecone_index = get_or_create_pinecone_index()


vector_store = PineconeVectorStore(
    index=pinecone_index,
    embedding=embeddings,
)


graph = Neo4jGraph(
    url=settings.NEO4J_URI,
    username=settings.NEO4J_USERNAME,
    password=settings.NEO4J_PASSWORD,
    database=settings.NEO4J_DATABASE,
)