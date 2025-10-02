import traceback

import MySQLdb
import pg8000
import pyodbc
import oracledb

class QueryRunner:
    # -------------------
    # Execute SQL Query
    # -------------------
    def execute_query(db_credentials: dict, sql_query: str):
        try:
            user = db_credentials["user"]
            password = db_credentials["password"]
            host = db_credentials["host"]
            port = db_credentials["port"]
            database = db_credentials["database"]
            db_type = db_credentials["db_type"]

            conn = None
            if db_type.upper() == "MYSQL":
                conn = MySQLdb.connect(user=user, password=password, host=host, port=int(port), db=database)
            elif db_type.upper() == "POSTGRESQL":
                conn = pg8000.connect(user=user, password=password, host=host, port=int(port), database=database)
            elif db_type.upper() == "MSSQL":
                conn = pyodbc.connect(
                    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                    f"SERVER={host},{port};DATABASE={database};UID={user};PWD={password};"
                    f"TrustServerCertificate=yes;Encrypt=yes;"
                )
            elif db_type.upper() == "ORACLE":
                conn = oracledb.connect(user=user, password=password, host=host, port=int(port), service_name=database)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            result = []
            # Execute the sql query
            with conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute(sql_query)
                        # Get column names from the cursor description
                        columns = [column[0] for column in cur.description]
                        
                        # Fetch all rows and convert each row to a dictionary
                        for row in cur.fetchall():
                            result.append(dict(zip(columns, row)))
                except Exception as e:
                    print("SQL Execution Error:", str(e))
            return result
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)
            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)
    
    # --------------------------
    # Check for Unsafe Queries
    # --------------------------
    def is_safe_query(query: str) -> bool:
        try:
            unsafe_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
            q_upper = query.upper()
            return not any(keyword in q_upper for keyword in unsafe_keywords)
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)
            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)