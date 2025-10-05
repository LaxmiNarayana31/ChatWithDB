import os
import re
import time
from sqlalchemy.exc import OperationalError

import streamlit as st
from jinja2 import Template

from app.prompts.summary_prompt import SUMMARY_PROMPT_TEMPLATE
from app.prompts.sql_prompt import SQL_PROMPT_TEMPLATE
from app.helpers.db_connector import connect_and_save_schema
from app.helpers.query_runner import QueryRunner
from app.helpers.llm_helper import get_llm_client


def main():
    st.set_page_config(page_title="Chat DB", layout="wide")

    # ---------------------------
    # Session State Initialization
    # ---------------------------
    defaults = {
        "page": "connect",
        "db_credentials": None,
        "db_schema_file": None,
        "query_response": None,
        "form_submitted": False,
        "generated_sql_query": None,
        "show_sql": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # ---------------------------
    # Connect Page
    # ---------------------------
    if st.session_state.page == "connect":
        col = st.columns([1, 2, 1])[1]
        with col:
            st.title("Connect to Your Database")
            
            # Only show the form if it hasn't been successfully submitted
            if not st.session_state.form_submitted:
                with st.form(key="db_connection_form"):
                    st.subheader("Enter Database Credentials")
                    db_type = st.selectbox("DB Type", ["MYSQL", "POSTGRESQL", "MSSQL", "ORACLE"])
                    host = st.text_input("Host")
                    user = st.text_input("User")
                    password = st.text_input("Password", type="password")
                    port = st.text_input("Port")
                    database = st.text_input("Database")
                    submitted = st.form_submit_button("Connect")

                    if submitted:
                        creds = {
                            "user": user,
                            "password": password,
                            "host": host,
                            "port": port,
                            "database": database,
                            "db_type": db_type,
                        }
                        try:
                            schema, schema_file = connect_and_save_schema(
                                user, password, host, port, database, db_type
                            )
                            st.session_state.db_credentials = creds
                            st.session_state.db_schema_file = schema_file
                            st.session_state.form_submitted = True
                            st.session_state.page = "chat"
                            # st.success(f"Connected!")
                            st.success("Connected! Redirecting to chat...")
                            # Delay slightly before rerun to give Streamlit time to update UI
                            time.sleep(0.5)
                            st.session_state.page = "chat"
                            st.rerun()
                        except OperationalError as e:
                            print(f"OperationalError: {e}")
                        except Exception as e:
                            st.error(f"Connection failed")

    # ---------------------------
    # Chat Page
    # ---------------------------
    elif st.session_state.page == "chat":
        col = st.columns([1, 2, 1])[1]
        with col:
            st.title("Chat with Your Database")

            if st.button("Disconnect"):
                # Reset all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

            st.subheader("Ask a question about your database")
            user_query = st.text_area("Enter your question:")

            if st.button("Send Query"):
                if not st.session_state.db_credentials:
                    st.error("No database connected!")
                else:
                    try:
                        SCHEMA_FOLDER = os.path.join(os.getcwd(), "schema")

                        # Read the .sql file from the schema folder
                        schema_filename = st.session_state.db_schema_file
                        schema_filepath = os.path.join(SCHEMA_FOLDER, schema_filename)
                        
                        # Load schema safely
                        if not os.path.exists(schema_filepath):
                            st.error("Session expired! Please reconnect to your database.")
                            
                            # Show countdown
                            placeholder = st.empty()
                            for i in range(10, 0, -1):
                                placeholder.info(f"Redirecting to connection page in {i} seconds...")
                                time.sleep(1)

                            # Reset session so user must reconnect
                            for key in list(st.session_state.keys()):
                                del st.session_state[key]

                            st.rerun()
                            return
                        
                        # Load schema
                        with open(schema_filepath, "r", encoding="utf-8") as f:
                            db_schema = f.read() 

                        # Initialize LLM client for SQl
                        llm = get_llm_client(task_type="query")

                        # ---------------------------
                        # Generate SQL via LLM
                        # ---------------------------
                        sql_prompt = Template(SQL_PROMPT_TEMPLATE).render(
                            question=user_query,
                            database_type=st.session_state.db_credentials["db_type"],
                            database_name=st.session_state.db_credentials["database"],
                        )
                        final_prompt = sql_prompt + "\n\n**Database Schema:**\n" + db_schema
                        sql_response = llm.invoke(final_prompt)
                        generated_sql_query = sql_response.content.strip()

                        # Extract SQL cleanly if wrapped in ```sql ... ```
                        match = re.search(r"```(?:sql)?\s*(.*?)\s*```", generated_sql_query, re.S)
                        if match:
                            generated_sql_query = match.group(1).strip()

                        # Save to session for "Show SQL" button
                        st.session_state.generated_sql_query = generated_sql_query

                        # ---------------------------
                        # Validate + Run SQL
                        # ---------------------------
                        if not QueryRunner.is_safe_query(generated_sql_query):
                            st.error("Unsafe query detected. Execution blocked.")
                            return

                        result_rows = QueryRunner.execute_query(
                            st.session_state.db_credentials,
                            generated_sql_query,
                        )
                        preview_rows = result_rows[:5] if isinstance(result_rows, list) else []

                        # ---------------------------
                        # Summarize Results via LLM
                        # ---------------------------
                        llm = get_llm_client(task_type="markdown")
                        result_prompt = Template(SUMMARY_PROMPT_TEMPLATE).render(
                            user_question=user_query,
                            generated_sql=generated_sql_query,
                            total_results=len(result_rows) if isinstance(result_rows, list) else 0,
                            preview_rows=preview_rows,
                        )

                        result_response = llm.invoke(result_prompt)
                        st.session_state.query_response = result_response.content

                    except Exception as e:
                        st.error(f"Query failed: {str(e)}")

            if st.session_state.query_response:
                st.markdown(st.session_state.query_response)

                # ---------------------------
                # Show SQL Button
                # ---------------------------
                if st.session_state.generated_sql_query:
                    if st.button("Show SQL Query"):
                        st.session_state.show_sql = not st.session_state.show_sql

                    if st.session_state.show_sql:
                        st.code(st.session_state.generated_sql_query, language="sql")