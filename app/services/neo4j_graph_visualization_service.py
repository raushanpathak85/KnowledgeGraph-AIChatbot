import os
import uuid
from typing import Dict, Any, List

from neo4j import GraphDatabase
from pyvis.network import Network

from app.config import settings


driver = GraphDatabase.driver(
    uri=settings.NEO4J_URI,
    auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
)


def fetch_neo4j_graph(
    cypher: str = "MATCH (s)-[r]->(t) RETURN s,r,t LIMIT 50",
) -> List[Dict[str, Any]]:
    records = []

    with driver.session(database=settings.NEO4J_DATABASE) as session:
        result = session.run(cypher)

        for record in result:
            s = record["s"]
            r = record["r"]
            t = record["t"]

            source_name = (
                s.get("id")
                or s.get("name")
                or s.get("title")
                or str(s.element_id)
            )

            target_name = (
                t.get("id")
                or t.get("name")
                or t.get("title")
                or str(t.element_id)
            )

            records.append(
                {
                    "source": source_name,
                    "source_label": list(s.labels)[0] if s.labels else "Node",
                    "relationship": r.type,
                    "target": target_name,
                    "target_label": list(t.labels)[0] if t.labels else "Node",
                }
            )

    return records


def generate_neo4j_graph_html(
    cypher: str = "MATCH (s)-[r]->(t) RETURN s,r,t LIMIT 50",
    output_dir: str = "static/graphs",
):
    os.makedirs(output_dir, exist_ok=True)

    graph_records = fetch_neo4j_graph(cypher)

    graph_id = f"neo4j_{uuid.uuid4()}"
    output_file = os.path.join(output_dir, f"{graph_id}.html")

    net = Network(
        height="1200px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#222222",
        font_color="white",
        filter_menu=True,
        cdn_resources="remote",
    )

    added_nodes = set()

    for row in graph_records:
        source = row["source"]
        target = row["target"]

        if source not in added_nodes:
            net.add_node(
                source,
                label=source,
                title=row["source_label"],
                group=row["source_label"],
            )
            added_nodes.add(source)

        if target not in added_nodes:
            net.add_node(
                target,
                label=target,
                title=row["target_label"],
                group=row["target_label"],
            )
            added_nodes.add(target)

        net.add_edge(
            source,
            target,
            label=row["relationship"],
            title=row["relationship"],
        )

    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -100,
          "centralGravity": 0.01,
          "springLength": 200,
          "springConstant": 0.08
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      }
    }
    """)

    net.save_graph(output_file)

    return {
        "graph_id": graph_id,
        "url": f"/static/graphs/{graph_id}.html",
        "file_path": output_file,
        "nodes_count": len(added_nodes),
        "edges_count": len(graph_records),
        "records": graph_records,
    }