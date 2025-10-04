# ChatWithDB

ChatWithDB is a Streamlit application for interactively querying relational databases using natural language. It:

- Connects to a database (MySQL, PostgreSQL, MSSQL, Oracle).
- Extracts the database schema and saves it temporarily to disk.
- Uses an LLM to convert user questions into safe, read-only SQL queries.
- Executes validated queries and summarizes preview results.

The app is intended for local development and experimentation with non-production data.

## Repository layout

```
Hackathon/
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
└── schema/                       # Temporary schema files written on connect
```

## Prerequisites

- Python 3.11+ (for local / non-Docker)
- Docker (if using Docker)
- Access to a test/dev database (MySQL, PostgreSQL, MSSQL or Oracle)
- An LLM API key: the project expects `CEREBRAS_API_KEY` (used by `app/helpers/llm_helper.py`).

## Environment variables

Create a `.env` file in the project root (same folder as `main.py`) and add:

```
CEREBRAS_API_KEY=your_cerebras_api_key_here
# Add any other provider credentials here if you change the LLM helper
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

Notes (non-Docker):

- The app writes temporary schema files to the `schema/` folder and deletes them after ~1 hour.
- If the schema file expires while you're in a session you will be prompted to reconnect.

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

Notes (Docker):

- Database drivers that require system libraries (e.g., Oracle Instant Client) may need extra setup in the Docker image. The provided Dockerfile includes common runtime packages but you may need to adjust it for your DB.
- The `schema/` directory inside the container is ephemeral. If you want to persist it for debugging, mount a host volume: `-v ${PWD}/schema:/app/schema`.

## Security & best practices

- Do not use production credentials while testing. Limit network access to test databases.
- Treat the `schema/` files as sensitive. They are automatically removed after one hour, but still store metadata about your DB.
- Review generated SQL before executing against critical systems.

## License

No license file is included. Add a `LICENSE` if you plan to publish or share this project publicly.

---
