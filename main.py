import os
from app.streamlit import streamlit_app

# Folder to store schema files
SCHEMA_FOLDER = os.path.join(os.getcwd(), "schema")
os.makedirs(SCHEMA_FOLDER, exist_ok=True)

if __name__ == "__main__":
    streamlit_app.main()
