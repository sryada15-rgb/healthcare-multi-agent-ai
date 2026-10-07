# Healthcare Multi-Agent AI

A production-style **multi-agent healthcare support system** built with **FastAPI, LangGraph, PostgreSQL, Redis, Milvus, Sentence Transformers, Docker, and optional AWS Bedrock Claude**.

The project demonstrates how specialized AI agents can collaborate to answer healthcare administrative questions involving **claims, benefits/policy coverage, and prior authorization**, while grounding responses in structured data and retrieved policy documents.

> **Important:** This repository is an educational/portfolio project and uses synthetic data only. It is not intended for medical diagnosis, treatment, or production handling of PHI/PII.

## Key Features

- Multi-agent orchestration with LangGraph
- Supervisor-driven intent identification
- Claims lookup from PostgreSQL
- Prior-authorization lookup from PostgreSQL
- Policy RAG using Milvus vector search
- MiniLM embeddings with Sentence Transformers
- Redis-backed short-term conversation history
- Optional response generation with Claude through AWS Bedrock
- PostgreSQL audit logging
- FastAPI REST API with Swagger documentation
- Docker Compose environment for PostgreSQL, Redis, Milvus, etcd, and MinIO
- Synthetic healthcare data for local testing

## Architecture

```text
                           User / Client
                                |
                                v
                         FastAPI /chat
                                |
                                v
                        Security / Input
                           Validation
                                |
                                v
                       LangGraph Supervisor
                                |
              +-----------------+------------------+
              |                 |                  |
              v                 v                  v
        Claims Agent      Prior Auth Agent    Policy RAG Agent
              |                 |                  |
              v                 v                  v
         PostgreSQL        PostgreSQL            Milvus
              |                 |                  |
              |                 |          Sentence Transformers
              |                 |             Embeddings
              +-----------------+------------------+
                                |
                                v
                         Response Agent
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
        Optional AWS Bedrock             Redis Memory
             Claude                     Conversation
                 |
                 v
          Grounded Response
                 |
                 v
        PostgreSQL Audit Log
```

## Agents

### Security / Input Validation
Performs basic request validation before the workflow reaches the specialist agents. In a production healthcare system, this layer would be expanded with authentication, authorization, PHI/PII masking, prompt-injection detection, and role-based tool permissions.

### Supervisor Agent
Analyzes the user's question and identifies relevant intents such as claims, policy/benefits, or prior authorization. LangGraph coordinates the workflow across the specialist nodes.

### Claims Agent
Retrieves structured claim information from PostgreSQL, including claim status and denial-related information.

### Prior Authorization Agent
Checks stored authorization information related to the member/claim and contributes authorization context to the final response.

### Policy RAG Agent
Retrieves relevant healthcare policy passages from Milvus. Policy text is converted into vector embeddings using Sentence Transformers and searched semantically at query time.

### Response Agent
Combines structured database facts and retrieved policy context into a final grounded response. AWS Bedrock Claude can optionally be enabled for LLM-based response generation.

## Why PostgreSQL, Redis, and Milvus?

Each storage technology has a different responsibility:

| Technology | Responsibility |
| --- | --- |
| PostgreSQL | Durable structured data such as claims, prior authorizations, and audit records |
| Redis | Short-term conversation history and session context |
| Milvus | Vector storage and semantic retrieval over healthcare policy documents |
| MinIO | Object storage used by standalone Milvus |
| etcd | Metadata/configuration dependency used by standalone Milvus |

This separation mirrors a common production pattern: relational databases for transactional facts, a low-latency store for session state, and a vector database for unstructured knowledge retrieval.

## Example Workflow

Example question:

```text
Why was my MRI claim denied and does my policy cover MRI?
```

Conceptual flow:

```text
1. FastAPI receives the request.
2. Security/input validation runs.
3. Supervisor identifies claim + policy/benefits intent.
4. Claims Agent retrieves CLM123 from PostgreSQL.
5. Prior Authorization Agent checks authorization information.
6. Policy RAG Agent searches Milvus for MRI-related policy context.
7. Response Agent combines the retrieved facts.
8. Redis stores recent conversation context.
9. PostgreSQL records an audit entry.
```

## Tech Stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| Agent orchestration | LangGraph |
| LLM | AWS Bedrock Claude (optional) |
| Embeddings | Sentence Transformers / MiniLM |
| Vector database | Milvus |
| Relational database | PostgreSQL |
| Conversation memory | Redis |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Infrastructure | Docker Compose |
| Milvus dependencies | etcd + MinIO |

## Project Structure

```text
healthcare-multi-agent-ai/
├── app/
│   ├── agents/
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   └── state.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── database.py
│   │   └── seed.py
│   ├── models/
│   │   ├── db_models.py
│   │   └── schemas.py
│   ├── rag/
│   │   └── milvus_store.py
│   ├── services/
│   │   ├── llm.py
│   │   └── redis_memory.py
│   └── main.py
├── data/
│   └── policies.json
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Prerequisites

Install:

- Python 3.11 recommended
- Docker Desktop
- Git
- VS Code (recommended)

## Local Setup

Clone the repository:

```bash
git clone https://github.com/sryada15-rgb/healthcare-multi-agent-ai.git
cd healthcare-multi-agent-ai
```

### Windows PowerShell

Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create the local environment file:

```powershell
Copy-Item .env.example .env
```

> Do not commit `.env`. Keep credentials and secrets out of Git.

## Start the Infrastructure

Start PostgreSQL, Redis, Milvus, etcd, and MinIO:

```powershell
docker compose up -d
```

Verify the containers:

```powershell
docker compose ps
```

Expected services include:

```text
postgres
redis
etcd
minio
milvus
```

## Start FastAPI

```powershell
python -m uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Use `POST /chat` to test the agent workflow.

## Test Requests

### Claims question

```json
{
  "conversation_id": "claim-test-001",
  "member_id": "MEM001",
  "claim_id": "CLM123",
  "message": "Why was claim CLM123 denied?"
}
```

### Policy / benefits question

```json
{
  "conversation_id": "policy-test-001",
  "member_id": "MEM001",
  "claim_id": "CLM123",
  "message": "Does my policy cover MRI scans?"
}
```

### Prior-authorization question

```json
{
  "conversation_id": "auth-test-001",
  "member_id": "MEM001",
  "claim_id": "CLM123",
  "message": "Did my MRI require prior authorization?"
}
```

### Multi-agent question

```json
{
  "conversation_id": "multi-agent-001",
  "member_id": "MEM001",
  "claim_id": "CLM123",
  "message": "Why was my MRI claim denied and does my policy cover MRI?"
}
```

This request demonstrates the main purpose of the project: combining structured claim information with authorization data and policy retrieval in one agent workflow.

### Conversation-memory test

Send a first message:

```json
{
  "conversation_id": "memory-001",
  "member_id": "MEM001",
  "claim_id": "CLM123",
  "message": "Why was claim CLM123 denied?"
}
```

Then reuse the same `conversation_id`:

```json
{
  "conversation_id": "memory-001",
  "member_id": "MEM001",
  "claim_id": "CLM123",
  "message": "What should I do about it?"
}
```

This exercises the Redis-backed conversation context.

## Enable AWS Bedrock Claude (Optional)

The application can run without Bedrock. The default `.env.example` contains:

```env
USE_BEDROCK=false
```

To enable Bedrock:

1. Configure AWS credentials locally using an appropriate AWS credential mechanism.
2. Ensure your AWS account/region has access to the selected Bedrock model.
3. Set `AWS_REGION` and `BEDROCK_MODEL_ID` in `.env`.
4. Change:

```env
USE_BEDROCK=true
```

5. Restart FastAPI.

Do not commit AWS credentials to this repository.

## RAG Flow

```text
Synthetic Policy Documents
          |
          v
Sentence Transformer
     Embeddings
          |
          v
        Milvus
          |
          | semantic similarity search
          v
Relevant Policy Context
          |
          v
    Response Agent
```

The current project demonstrates semantic vector retrieval. A production evolution could add BM25 keyword retrieval, metadata filtering, cross-encoder reranking, citation validation, and retrieval evaluation.

## Stop the Environment

Stop containers while preserving their volumes:

```powershell
docker compose down
```

Stop containers and delete local persisted database/vector data:

```powershell
docker compose down -v
```

## Production Evolution

This repository intentionally focuses on a locally runnable architecture. A production healthcare implementation should add:

- OAuth/OIDC authentication
- Role-based access control and tool authorization
- PHI/PII detection and masking
- Prompt-injection and tool-abuse defenses
- Secrets Manager or equivalent secret storage
- TLS and private networking
- Hybrid retrieval (BM25 + vector search)
- Cross-encoder reranking
- Metadata/tenant filtering
- Conditional or parallel LangGraph routing
- Human-in-the-loop approval for consequential actions
- RAG evaluation with Recall@K, Precision@K, MRR, RAGAS, or DeepEval
- Agent routing/tool-selection evaluation
- Langfuse or equivalent LLM tracing
- Prometheus/Grafana/CloudWatch observability
- CI/CD and automated tests
- Kubernetes/EKS deployment

## Limitations

- Uses synthetic healthcare data only.
- It is a demonstration system, not a clinical decision-support system.
- It should not be used for diagnosis, treatment, or real member coverage decisions.
- The current RAG implementation is intentionally simplified for local development.
- Production-grade authorization, PHI controls, evaluation, and human review are future enhancements.

## Disclaimer

This project is for educational, demonstration, and portfolio purposes. It does not provide medical advice and must not be used with real protected health information without appropriate security, privacy, compliance, and governance controls.
