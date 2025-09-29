# TODO
- [ ] Write tests for each service.
- [ ] Create a web UI for the app.

# VIE Law Assistant
VIE Law Assistant is a modular, containerized system designed to provide legal information retrieval and conversational AI services for Vietnamese law documents. It leverages large language models (LLMs), document retrievers, and caching/rate-limiting mechanisms to deliver fast, accurate, and scalable legal assistance.

### Features
- Conversational AI: Chatbot interface for querying Vietnamese law documents.
- Document Retrieval: Efficient retrieval of relevant legal documents using embeddings (both dense and sparse) and vector search.
- PDF Processing: Automatic ingestion and indexing of legal PDFs.
Caching & Rate Limiting: High-performance caching and request rate limiting using Valkey.
- Microservices Architecture: Decoupled services for LLM and retriever, orchestrated via Docker Compose.

### Project Structure
```
├── configs/                    # Valkey configuration files
├── data/
│   ├── pdfs/                   # Source PDFs for ingestion
|   ├── qdrant/                 # Vector DB
│   └── valkey-cache/           # Valkey data for caching
│   └── valkey-rate-limit/      # Valkey data for rate limiting
├── services/
│   ├── llm-service/            # LLM-based chat completion service
│   └── retriever-service/      # Document retrieval and indexing service
├── frontend/                   # Web UI of the app
├── docker-compose.yaml         # Docker Compose orchestration
└── README.md                   # Project documentation
```

### Services Overview
#### LLM Service
Provides chat completion and conversational AI endpoints.
Built with FastAPI and Python.
Handles user queries and interacts with the retriever service.
#### Retriever Service
Handles document ingestion, embedding, and retrieval.
Processes PDFs and builds vector indices for fast search.
Exposes endpoints for document search and indexing.
#### Valkey (Cache & Rate Limiting)
Used for caching responses and enforcing rate limits.
Configured via ``valkey-cache.conf`` and ``valkey-rate-limit.conf``.


### Getting Started
#### Prerequisites
- Docker
- Docker Compose


### Setup & Run
1. Clone the repository:
```
git clone https://github.com/NgocDuy3112/vie-law-assistant.git
cd vie-law-assistant
```
2. Add your legal PDFs: Place your PDF files in the pdfs directory.
3. Start the services:
```
docker-compose up --build
```

4. Access the Web UI and APIs:
- **Frontend (Web UI):** http://localhost:3000
- **LLM Service API:** http://localhost:8001/docs
- **Retriever Service API:** http://localhost:8000/docs


### Development
Python dependencies for each service are listed in their respective requirements.txt files.



### Configuration
- **Frontend:** Static files are in the `frontend/` directory. Nginx config is at `frontend/nginx.conf` (edit for SPA routing or CORS if needed).
- **Valkey:** Edit configs in `configs` as needed.
- **Service settings:** Adjust environment variables in `docker-compose.yaml` or service config files.


### Acknowledgements
- FastAPI
- Valkey
- Docker
- PostgreSQL
- Qdrant
- Nginx