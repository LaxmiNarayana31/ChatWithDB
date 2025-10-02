import json
import traceback

from sqlalchemy.engine import create_engine
from urllib.parse import quote_plus
from langchain_community.utilities.sql_database import SQLDatabase

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
        # print("==============================================")
        # print(db_schema)
        # print("==============================================")

        schema_file = f"{database}_{db_type}.sql"
        with open(schema_file, "w", encoding="utf-8") as f:
            f.write(db_schema)
        return db_schema, schema_file
    except Exception as e:
        # Get the traceback as a string
        traceback_str = traceback.format_exc()
        print(traceback_str)
        # Get the line number of the exception
        line_no = traceback.extract_tb(e.__traceback__)[-1][1]
        print(f"Exception occurred on line {line_no}")
        return str(e)