from pinecone import Pinecone, ServerlessSpec

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_neo4j import Neo4jGraph
from langchain_pinecone import PineconeVectorStore

from app.config import settings


llm = ChatOpenAI(
    model=settings.LLM_MODEL,
    temperature=0,
    api_key=settings.OPENAI_API_KEY,
)

embeddings = OpenAIEmbeddings(
    model=settings.EMBEDDING_MODEL,
    api_key=settings.OPENAI_API_KEY,
)


pc = Pinecone(api_key=settings.PINECONE_API_KEY)


def get_or_create_pinecone_index():
    existing_indexes = [index.name for index in pc.list_indexes()]

    if settings.PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=1536,
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