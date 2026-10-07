# Healthcare Multi-Agent AI

A VS Code-ready demo inspired by enterprise healthcare support workflows. It uses FastAPI + LangGraph with PostgreSQL, Redis, and Milvus.

## Architecture

User -> FastAPI -> Security -> Supervisor -> Claims Agent -> Prior Auth Agent -> Policy RAG Agent -> Response Agent

- PostgreSQL: claims, prior authorizations, audit logs
- Redis: short-term conversation history/cache
- Milvus: vector search over healthcare policy documents
- Sentence Transformers: MiniLM embeddings
- AWS Bedrock Claude: optional grounded response generation

> This is a learning/demo project with synthetic data. Do not use real PHI/PII.

## 1. Prerequisites

- VS Code
- Python 3.11 or 3.12 recommended
- Docker Desktop
- Git (optional)

## 2. Open in VS Code

Open this folder in VS Code, then open the integrated terminal.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, you can use the interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Start PostgreSQL, Redis, and Milvus

```powershell
docker compose up -d
```

Check containers:

```powershell
docker compose ps
```

## 4. Start FastAPI

```powershell
uvicorn app.main:app --reload
```

Open Swagger at `http://127.0.0.1:8000/docs`.

## 5. Test the multi-agent workflow

POST `/chat`:

```json
{
  "conversation_id": "demo-001",
  "member_id": "MEM001",
  "claim_id": "CLM123",
  "message": "Why was my MRI claim denied and does my policy cover MRI?"
}
```

Expected flow:

1. Security validates input.
2. Supervisor identifies claim + benefits intents.
3. Claims agent reads `CLM123` from PostgreSQL.
4. Prior-auth agent checks authorization data.
5. RAG agent searches policy vectors in Milvus.
6. Response agent combines grounded facts.
7. Redis saves recent conversation context.
8. PostgreSQL saves an audit record.

## 6. Enable AWS Bedrock Claude (optional)

The default `.env` has:

```env
USE_BEDROCK=false
```

This lets the project run without AWS. To use Bedrock, configure AWS credentials locally, choose a Bedrock model available to your account/region, update `BEDROCK_MODEL_ID`, then set:

```env
USE_BEDROCK=true
```

Restart FastAPI after changing `.env`.

## 7. Stop infrastructure

```powershell
docker compose down
```

To also delete local database/vector data:

```powershell
docker compose down -v
```

## Project structure

```text
app/
  agents/
    graph.py
    nodes.py
    state.py
  core/
    config.py
  db/
    database.py
    seed.py
  models/
    db_models.py
    schemas.py
  rag/
    milvus_store.py
  services/
    llm.py
    redis_memory.py
  main.py
data/
  policies.json
docker-compose.yml
requirements.txt
.env.example
```

## Production improvements

For a production healthcare deployment, add OAuth/OIDC authorization, role-based tool permissions, PHI/PII masking, prompt-injection defenses, TLS/secrets management, hybrid BM25 + vector retrieval, reranking, LangGraph conditional routing, human approval for consequential actions, evaluation with RAGAS/DeepEval, Langfuse tracing, and deployment to EKS.
