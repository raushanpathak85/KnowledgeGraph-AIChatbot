import re
from langchain_anthropic import ChatAnthropic

from app.config import settings


client = ChatAnthropic(
    model=settings.LLM_MODEL,
    temperature=0,
    anthropic_api_key=settings.ANTHROPIC_API_KEY,
)


def clean_cypher(text: str) -> str:
    text = text.strip()
    text = text.replace("```cypher", "")
    text = text.replace("```", "")
    text = text.replace("Cypher:", "")
    return text.strip()


def validate_readonly_cypher(cypher: str) -> bool:
    blocked_keywords = [
        "CREATE",
        "MERGE",
        "DELETE",
        "DETACH",
        "SET",
        "REMOVE",
        "DROP",
        "LOAD CSV",
        "CALL DBMS",
        "ALTER",
        "GRANT",
        "DENY",
        "REVOKE",
    ]

    upper_cypher = cypher.upper().strip()

    if not upper_cypher.startswith("MATCH"):
        return False

    if "RETURN" not in upper_cypher:
        return False

    for keyword in blocked_keywords:
        if re.search(rf"\b{keyword}\b", upper_cypher):
            return False

    return True


def prompt_to_cypher(user_prompt: str) -> str:
    system_prompt = """
You are a Neo4j Cypher expert.

Convert the user's natural language graph visualization request into a safe READ-ONLY Cypher query.

Database pattern:
- Nodes can have labels like __Entity__, Document, Company, Person, Topic, Sector, Report.
- Entity nodes usually have property id.
- Some nodes may have name or title.
- Relationships can be any type.

Rules:
- Return ONLY Cypher query.
- Do not explain.
- Only generate read-only MATCH queries.
- Always return s,r,t.
- Always limit results to 50 unless user asks smaller.
- Never use CREATE, MERGE, DELETE, SET, REMOVE, DROP, LOAD CSV, CALL, ALTER.

Examples:

User: show full graph
MATCH (s)-[r]->(t) RETURN s,r,t LIMIT 50

User: show graph for Tesla
MATCH (s)-[r]-(t)
WHERE toLower(coalesce(s.id, s.name, s.title, '')) CONTAINS 'tesla'
   OR toLower(coalesce(t.id, t.name, t.title, '')) CONTAINS 'tesla'
RETURN s,r,t LIMIT 50

User: show graph excluding mentions
MATCH (s)-[r]->(t)
WHERE type(r) <> 'MENTIONS'
RETURN s,r,t LIMIT 50

User: show documents connected to Tesla
MATCH (s)-[r]-(t)
WHERE (
  toLower(coalesce(s.id, s.name, s.title, '')) CONTAINS 'tesla'
  OR toLower(coalesce(t.id, t.name, t.title, '')) CONTAINS 'tesla'
)
RETURN s,r,t LIMIT 50
"""

    response = client.invoke(
        [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
    )

    cypher = clean_cypher(response.content)

    if not validate_readonly_cypher(cypher):
        raise ValueError(f"Generated unsafe or invalid Cypher: {cypher}")

    return cypher