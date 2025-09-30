import traceback

from sqlalchemy.engine import create_engine
from urllib.parse import quote_plus
from langchain_community.utilities.sql_database import SQLDatabase

def init_database_connection(user: str, password: str, host: str, port: str, database: str, db_type: str):
    try:
        encoded_password = quote_plus(password)
        database_conn_string = None

        if db_type.upper() == "MYSQL":
            database_conn_string = f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}"
        elif db_type.upper() == "POSTGRESQL":
            database_conn_string = f"postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{database}"
        elif db_type.upper() == "MSSQL":
            database_conn_string = f"mssql+pymssql://{user}:{encoded_password}@{host}:{port}/{database}"
        elif db_type.upper() == "ORACLE":
            database_conn_string = f"oracle+cx_oracle://{user}:{encoded_password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        engine = create_engine(database_conn_string)
        sql_database = SQLDatabase.from_uri(database_conn_string)
        return sql_database, engine, database
    except Exception as e:
        # Get the traceback as a string
        traceback_str = traceback.format_exc()
        print(traceback_str)
        # Get the line number of the exception
        line_no = traceback.extract_tb(e.__traceback__)[-1][1]
        print(f"Exception occurred on line {line_no}")
        return str(e)