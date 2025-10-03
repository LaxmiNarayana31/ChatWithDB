# ChatWithDB

ChatWithDB is a Streamlit application that lets you connect to a relational database, automatically extracts the database schema, and uses an LLM to convert natural-language questions into safe, read-only SQL queries and present a short summary of results.

The app is designed for experimentation and prototyping: connect to a dev/test database, ask questions in plain English and get back executable SQL and summarized results (preview rows only). The schema is stored temporarily on disk and automatically removed after an hour.

## Key features

- Connect to common relational databases (MySQL, PostgreSQL, MSSQL, Oracle).
- Automatic schema extraction using SQLAlchemy + langchain_community utilities.
- Natural language -> SQL generation via an LLM (Cerebras model configured by environment variables).
- Safety: LLM is instructed to produce read-only queries.
- Result summarization (Markdown) using a second LLM pass.

## Folder structure

Top-level layout (important files/folders):

```
Hackathon/
├── main.py                       # Lightweight runner that calls the Streamlit app
├── README.md                     # This file
├── requirement.txt               # Python dependencies (install with pip)
├── packages.txt                  # Optional additional package list (if present)
├── pyproject.toml                # Project metadata (if present)
├── app/
│   ├── helpers/
│   │   ├── db_connector.py       # Connects to DB and saves schema to /schema
│   │   ├── llm_helper.py         # LLM client factory (uses CEREBRAS_API_KEY env var)
│   │   ├── query_runner.py       # Executes queries and safety checks
│   │   └── ...
│   ├── prompts/
│   │   ├── sql_prompt.py         # Template used to instruct the LLM for SQL generation
│   │   └── summary_prompt.py     # Template for result summarization
│   └── streamlit/
│       └── streamlit_app.py      # Streamlit UI and application flow
└── schema/                       # Temporary schema files created on connect
```

## Quickstart (Windows / PowerShell)

1. Install Python (3.11+ recommended). Open PowerShell (`pwsh.exe`).

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies. The repository includes `requirement.txt` and `packages.txt`—install whichever file you maintain. Example:

```powershell
pip install --upgrade pip
pip install -r requirement.txt
# If you also have packages.txt and want to install it:
# pip install -r packages.txt
```

Note: Some database drivers (see below) are optional and only needed for the DB type you plan to connect to.

4. Create a `.env` file in the project root (same folder as `main.py`) and add your LLM API key(s). At minimum the app expects:

```
CEREBRAS_API_KEY=your_cerebras_api_key_here
```

The code uses python-dotenv to load environment variables.

5. Run the Streamlit app. You can run the app directly with Streamlit so it launches a local web server:

```powershell
streamlit run main.py
```

Opening that will show the Connect page where you can enter database credentials.

(Alternatively you can run `python main.py`, but `streamlit run` is the usual pattern for Streamlit apps.)

## Supported databases and driver notes

The app supports the following DB types (the selection list is shown in the UI):

- MYSQL
- POSTGRESQL
- MSSQL
- ORACLE

Driver strings used in `app/helpers/db_connector.py`:

- MySQL: `mysql+mysqldb://` (requires a MySQL DB driver such as `mysqlclient` / `MySQL-python`)
- PostgreSQL: `postgresql+psycopg2://` (install `psycopg2-binary`)
- MSSQL: `mssql+pymssql://` (install `pymssql`)
- Oracle: `oracle+cx_oracle://` (install `cx_Oracle` and Oracle client libraries)

Install only the DB drivers you need. Example pip installs (PowerShell):

```powershell
pip install psycopg2-binary      # PostgreSQL
pip install mysqlclient          # MySQL (may need Visual C++ / build tools on Windows)
pip install pymssql              # MSSQL
# Oracle requires cx_Oracle + Oracle Instant Client (follow cx_Oracle docs)
```

If you run into issues installing `mysqlclient` on Windows, you can use `PyMySQL` with a connection string modification or install precompiled wheels.

## How it works (high-level)

1. User opens the app and fills the connection form (DB type, host, port, user, password, database).
2. Backend connects using SQLAlchemy and extracts a textual schema dump using `langchain_community.utilities.sql_database.SQLDatabase`.
3. Schema is saved to `schema/{database}_{db_type}.sql` and scheduled for deletion after 1 hour.
4. When the user asks a question, the app:
   - Loads the saved schema file and the question.
   - Uses the LLM (configured in `app/helpers/llm_helper.py`) to generate a single, read-only SQL query.
   - Validates the generated SQL for safety via `app/helpers/query_runner.py`.
   - Executes the query and shows a preview (first 5 rows).
   - Summarizes the preview rows using an LLM prompt template and displays the summary in Markdown.

## Important security & safety notes

- The app is intended for local/dev use only. Do not point it at production databases with sensitive data unless you fully understand the risk.
- Schema files are written to the `schema/` folder and automatically deleted after one hour. Still treat them as sensitive.
- The LLM is instructed via prompts to produce read-only SQL. The app also runs a safety check before executing queries, but you should review any generated SQL before running it against sensitive systems.

## Where to look / developer notes

- SQL prompt template: `app/prompts/sql_prompt.py` — controls how the LLM is asked to output SQL (very strict: only a code block and read-only SQL).
- Summary prompt: `app/prompts/summary_prompt.py` — controls the result summarization style.
- DB connector: `app/helpers/db_connector.py` — creates the SQLAlchemy engine and extracts/saves schema.
- LLM client: `app/helpers/llm_helper.py` — returns an LLM client. It reads `CEREBRAS_API_KEY` from environment.
- Streamlit UI: `app/streamlit/streamlit_app.py` — the main UI and flow.

If you modify prompts or the LLM selection, be careful to preserve the safety rules in `sql_prompt.py`.

## Troubleshooting

- Streamlit not found: make sure you installed `streamlit` into the activated virtualenv.
- DB connection fails: confirm host/port, network access, username/password and correct DB driver installed.
- LLM errors: confirm `CEREBRAS_API_KEY` is present in the environment and that the model name/config in `llm_helper.py` is supported by your account.
- Schema file missing after connect: the schema file is deleted after one hour. Reconnect to refresh.

## License & contact

This repository does not include a license file. Add a `LICENSE` if you plan to publish or share.

For questions about running or developing this app, inspect the files under `app/` and open an issue or contact the project maintainer.