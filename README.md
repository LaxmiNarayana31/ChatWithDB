# ChatWithDB

ChatWithDB is a Streamlit app that lets you query databases using natural language. It connects to MySQL, PostgreSQL, MSSQL, or Oracle and uses Large Language Models (LLMs) to:

- Convert questions into safe, read-only SQL queries
- Execute and summarize query results for easy interpretation

## LLM Integration
Powered by the Cerebras API, ChatWithDB uses:

- `gpt-oss-120b` for SQL generation
- `llama3.1-8b` for summarization and markdown output

## Repository layout

```
├── main.py                       # Entrypoint that launches the Streamlit app
├── README.md
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container recipe (provided)
├── app/
│   ├── helpers/
│   │   ├── db_connector.py       # Connects to DB and saves schema to /schema
│   │   ├── llm_helper.py         # LLM client factory (reads CEREBRAS_API_KEY)
│   │   ├── query_runner.py       # Executes queries and safety checks
│   ├── prompts/
│   │   ├── sql_prompt.py         # Prompt template for SQL generation
│   │   └── summary_prompt.py     # Prompt template for result summarization
│   └── streamlit/
│       └── streamlit_app.py      # Streamlit UI and app flow
```

## Prerequisites

- Python 3.11+ (for local / non-Docker)
- Docker (if using Docker)
- Access to a test/dev database (MySQL, PostgreSQL, MSSQL or Oracle)
- An LLM API key: the project expects `CEREBRAS_API_KEY`

## Environment variables

Create a `.env` file in the project root (same folder as `main.py`) and add:

```
CEREBRAS_API_KEY=your_cerebras_api_key_here
```

## Run without Docker (recommended for development)

1. Open terminal in the project root.

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. Create `.env` with `CEREBRAS_API_KEY` (see above).

5. Start the Streamlit app:

```powershell
streamlit run main.py
```

Open the URL shown by Streamlit (usually http://localhost:8501) and use the Connect form.

## Run with Docker

The repository includes a `Dockerfile` designed to build an image with the runtime and required packages. The Dockerfile installs common client dependencies (MariaDB, unixODBC, etc.).

Build the image (from the project root):

```powershell
# Replace <tag> with the image name you want, e.g. chatwithdb:latest
docker build -t chatwithdb:latest .
```

Run the container (recommended: pass the LLM API key via env and map port 8501):

```powershell
docker run --rm -it \
   -e CEREBRAS_API_KEY="your_cerebras_api_key_here" \
   -p 8501:8501 \
   --name chatwithdb_local \
   chatwithdb:latest
```

If you prefer to mount a local `.env` or the entire repo into the container (so changes are picked up), use a volume:

```powershell
docker run --rm -it \
   --env-file .env \
   -v ${PWD}:/app \
   -p 8501:8501 \
   chatwithdb:latest
```

## Security & best practices

- Do not use production credentials while testing. Limit network access to test databases.
- Review generated SQL before executing against critical systems.

## License

This project is open source and intended for learning and development purposes. You are free to use, modify, and share the code under a permissive license (such as MIT or Apache 2.0). If you plan to publish or distribute this project, please add a `LICENSE` file to clarify the terms and ensure compliance with open source best practices.
---
