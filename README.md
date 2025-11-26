# Medical Chatbot with LLMs, LangChain, Pinecone & Flask

A comprehensive medical AI assistant utilizing RAG (Retrieval Augmented Generation) with Pinecone vector database and OpenAI's GPT models.

## Features
-  **Interactive Chat**: Real-time Q&A with context from medical documents
-  **Voice Interaction**: Speech-to-Text and Text-to-Speech capabilities
-  **RAG Architecture**: Accurate answers grounded in provided PDF data
-  **Production Ready**: Includes caching, monitoring, and WSGI deployment setup

## Quick Start

### 1. Prerequisites
- Python 3.10+
- Pinecone Account & API Key
- OpenAI Account & API Key
 
# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```ini
PINECONE_API_KEY=your_pinecone_key
OPENAI_API_KEY=your_openai_key

# Optional Monitoring
# LANGCHAIN_TRACING=true
# LANGSMITH_API_KEY=your_key
# SENTRY_DSN=your_dsn
```

### 4. Data Ingestion
Index your PDF documents (place them in `data/` folder):
```bash
python store_index.py
```

### 5. Running the Application

**Development:**
```bash
python app.py
```

**Production:**
```bash
# Uses Waitress (included in requirements)
python wsgi.py
```
Access at `http://localhost:8080`

## Deployment

### Docker
1. Build image: `docker build -t medical-bot .`
2. Run container: `docker run -p 8080:8080 --env-file .env medical-bot`

### AWS / Cloud
See `IMPLEMENTATION_SUMMARY.md` for detailed cloud architecture notes. The project is ready for AWS EC2/ECR deployment via GitHub Actions.


<!-- aws repo uri -->
URI: 845087561044.dkr.ecr.eu-north-1.amazonaws.com/medical-bot
845087561044.dkr.ecr.us-east-1.amazonaws.com/medical-chatbot