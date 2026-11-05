from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import uuid

client = QdrantClient(":memory:")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
COLLECTION = "critique_memory"

client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

def store_critique(persona: str, proposal: str, attack: str, severity: int):
    vector = embedder.encode(attack).tolist()
    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "persona": persona,
                    "proposal": proposal,
                    "attack": attack,
                    "severity": severity
                }
            )
        ]
    )

def recall_similar_attacks(query: str, persona: str, k: int = 2):
    vector = embedder.encode(query).tolist()
    results = client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=k,
        with_payload=True,
        query_filter=Filter(
            must=[FieldCondition(key="persona", match=MatchValue(value=persona))]
        )
    )
    attacks = []
    for point in results.points:
        if point.payload is not None:
            attacks.append(point.payload.get("attack", ""))
    return attacks