import os
import time
import traceback
import threading

from urllib.parse import quote_plus
from sqlalchemy.engine import create_engine
from langchain_community.utilities.sql_database import SQLDatabase

SCHEMA_FOLDER = os.path.join(os.getcwd(), "schema")

# ------------------------
# Delete file after delay
# ------------------------
def delete_file_after_delay(filepath: str, delay_seconds: int = 3600):
    try:    
        def delete():
            time.sleep(delay_seconds)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Failed to delete file: {filepath}, Error: {e}")
        threading.Thread(target=delete, daemon=True).start()
    except Exception as e:
        # Get the traceback as a string
        traceback_str = traceback.format_exc()
        print(traceback_str)
        # Get the line number of the exception
        line_no = traceback.extract_tb(e.__traceback__)[-1][1]
        print(f"Exception occurred on line {line_no}")
        return str(e)

# ------------------------
# Connect and Save Schema
# ------------------------
def connect_and_save_schema(user: str, password: str, host: str, port: str, database: str, db_type: str):
    try:
        encoded_password = quote_plus(password)
        conn_str = None

        if db_type.upper() == "MYSQL":
            conn_str = f"mysql+mysqldb://{user}:{encoded_password}@{host}:{port}/{database}"
        elif db_type.upper() == "POSTGRESQL":
            conn_str = f"postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{database}"
        elif db_type.upper() == "MSSQL":
            conn_str = f"mssql+pymssql://{user}:{encoded_password}@{host}:{port}/{database}"
        elif db_type.upper() == "ORACLE":
            conn_str = f"oracle+cx_oracle://{user}:{encoded_password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        engine = create_engine(conn_str, poolclass=None)
        sql_database = SQLDatabase(engine=engine, include_tables=None, sample_rows_in_table_info=0)

        db_schema = sql_database.get_table_info()

        # Create the schema file path
        schema_file = os.path.join(SCHEMA_FOLDER, f"{database}_{db_type}.sql")

        # Write to file
        with open(schema_file, "w", encoding="utf-8") as f:
            f.write(db_schema)

        # Schedule file for deletion after 1 hour (3600 seconds)
        delete_file_after_delay(schema_file, delay_seconds=3600)

        return db_schema, schema_file
    except Exception as e:
        # Get the traceback as a string
        traceback_str = traceback.format_exc()
        print(traceback_str)
        # Get the line number of the exception
        line_no = traceback.extract_tb(e.__traceback__)[-1][1]
        print(f"Exception occurred on line {line_no}")
        return str(e)