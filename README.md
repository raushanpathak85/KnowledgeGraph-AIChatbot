# KnowledgeGraph-AIChatbot

# Run Project
uvicorn app.main:app --reload

# Test Uploaded File
curl -X POST "http://localhost:8000/uploaded-files/ingest" \
  -F "file=@sample_report.pdf"

  # Test Reports Portal
  curl -X POST "http://localhost:8000/reports-portal/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "EV Market Outlook 2026",
    "content": "Tesla and BYD are competing in the EV market. Battery cost and China demand are major risks.",
    "source_url": "https://reports.portal/ev-market-2026",
    "author": "Analyst Team",
    "sector": "Automotive",
    "published_date": "2026-04-20"
  }'

  # Test Query
  curl -X POST "http://localhost:8000/query/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What risks are connected to Tesla and BYD in the EV market?",
    "top_k": 5
  }'


  # WorkFlow 
  Uploaded file / report
        ↓
  LangChain Document Loader
        ↓
  RecursiveCharacterTextSplitter
        ↓
  OpenAIEmbeddings
        ↓
  PineconeVectorStore
        ↓
  LLMGraphTransformer
        ↓
  Neo4jGraph
        ↓
  Hybrid KG + Vector RAG Answer