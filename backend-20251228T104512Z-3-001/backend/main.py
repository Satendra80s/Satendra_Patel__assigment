from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import defaultdict, deque
from typing import List

app = FastAPI()

# CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3003", "http://localhost:3000"],  
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str

class Edge(BaseModel):
    source: str
    target: str

class Pipeline(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

@app.post("/pipelines/parse")
def parse_pipeline(pipeline: Pipeline):
    node_ids = {node.id for node in pipeline.nodes}

    graph = defaultdict(list)
    indegree = {node_id: 0 for node_id in node_ids}

    for edge in pipeline.edges:
        if edge.source not in node_ids or edge.target not in node_ids:
            raise HTTPException(
                status_code=400,
                detail="Edge references non-existent node"
            )

        if edge.source == edge.target:
            return {
                "num_nodes": len(node_ids),
                "num_edges": len(pipeline.edges),
                "is_dag": False
            }

        graph[edge.source].append(edge.target)
        indegree[edge.target] += 1

    
    queue = deque([n for n in node_ids if indegree[n] == 0])
    visited = 0

    while queue:
        node = queue.popleft()
        visited += 1
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    return {
        "num_nodes": len(node_ids),
        "num_edges": len(pipeline.edges),
        "is_dag": visited == len(node_ids)
    }
