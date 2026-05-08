from pydantic_settings import BaseSettings


class Settings(BaseSettings):
     
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"

    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str = "neo4j"

    ANTHROPIC_API_KEY: str
    LLM_MODEL: str = "claude-sonnet-4-6"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    CHUNK_SIZE: int = 1200
    CHUNK_OVERLAP: int = 200

    class Config:
        env_file = ".env"


settings = Settings()