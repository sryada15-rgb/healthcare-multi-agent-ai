import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient, DataType
from app.core.config import get_settings

class PolicyStore:
    def __init__(self):
        s = get_settings()
        self.client = MilvusClient(uri=s.milvus_uri)
        self.collection = s.milvus_collection
        self.encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def ensure_collection(self):
        if self.client.has_collection(self.collection):
            return
        schema = self.client.create_schema(auto_id=True, enable_dynamic_field=False)
        schema.add_field("id", DataType.INT64, is_primary=True, auto_id=True)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=384)
        schema.add_field("policy_id", DataType.VARCHAR, max_length=100)
        schema.add_field("section", DataType.VARCHAR, max_length=200)
        schema.add_field("page", DataType.INT64)
        schema.add_field("text", DataType.VARCHAR, max_length=4000)
        index_params = self.client.prepare_index_params()
        index_params.add_index(field_name="vector", index_type="HNSW", metric_type="COSINE", params={"M": 16, "efConstruction": 200})
        self.client.create_collection(collection_name=self.collection, schema=schema, index_params=index_params)

    def ingest_sample_policies(self, path="data/policies.json"):
        self.ensure_collection()
        existing = self.client.query(self.collection, filter='policy_id != ""', output_fields=["policy_id"], limit=1)
        if existing:
            return
        docs = json.loads(Path(path).read_text())
        vectors = self.encoder.encode([d["text"] for d in docs], normalize_embeddings=True)
        rows = [{**d, "vector": v.tolist()} for d, v in zip(docs, vectors)]
        self.client.insert(self.collection, rows)

    def search(self, query: str, limit: int = 3) -> list[dict]:
        vector = self.encoder.encode([query], normalize_embeddings=True)[0].tolist()
        results = self.client.search(
            collection_name=self.collection,
            data=[vector],
            anns_field="vector",
            limit=limit,
            output_fields=["policy_id", "section", "page", "text"],
            search_params={"metric_type": "COSINE", "params": {"ef": 64}},
        )
        return [hit["entity"] | {"score": hit["distance"]} for hit in results[0]]
