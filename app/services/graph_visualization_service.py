import os
import uuid

from pyvis.network import Network
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer

from app.services.langchain_clients import llm


graph_transformer = LLMGraphTransformer(llm=llm)


async def extract_graph_data(text: str):
    documents = [Document(page_content=text)]
    graph_documents = await graph_transformer.aconvert_to_graph_documents(documents)
    return graph_documents


def visualize_graph(graph_documents, output_dir: str = "static/graphs"):
    os.makedirs(output_dir, exist_ok=True)

    graph_id = str(uuid.uuid4())
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

    if not graph_documents:
        return None

    nodes = graph_documents[0].nodes
    relationships = graph_documents[0].relationships

    node_dict = {node.id: node for node in nodes}

    valid_edges = []
    valid_node_ids = set()

    for rel in relationships:
        if rel.source.id in node_dict and rel.target.id in node_dict:
            valid_edges.append(rel)
            valid_node_ids.update([rel.source.id, rel.target.id])

    for node_id in valid_node_ids:
        node = node_dict[node_id]
        net.add_node(
            node.id,
            label=node.id,
            title=node.type,
            group=node.type,
        )

    for rel in valid_edges:
        net.add_edge(
            rel.source.id,
            rel.target.id,
            label=rel.type.lower(),
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
        "file_path": output_file,
        "url": f"/static/graphs/{graph_id}.html",
        "nodes_count": len(valid_node_ids),
        "edges_count": len(valid_edges),
    }


async def generate_knowledge_graph_html(text: str):
    graph_documents = await extract_graph_data(text)
    result = visualize_graph(graph_documents)
    return result