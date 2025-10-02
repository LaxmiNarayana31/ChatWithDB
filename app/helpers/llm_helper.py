import os
import traceback

from dotenv import load_dotenv
from langchain_cerebras.chat_models import ChatCerebras
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

load_dotenv(verbose=True)

# ------------------------------
# LLM Client for SQL Generation
# ------------------------------
def get_llm_client(task_type: str = "markdown"):
    """
    Returns an LLM client based on the task type.
    - task_type="query"     -> gpt-oss-120b (for SQL/query generation)
    - task_type="markdown"  -> llama3.1-8b (for summarization/markdown output)
    """
    try:
        # Centralized model config
        model_config = {
            "query": {
                "model": "gpt-oss-120b",
                "temperature": 0.7,
                "top_p": 0.9,
                "max_retries": 1,
            },
            "markdown": {
                "model": "llama3.1-8b",
                "temperature": 0.8,
                "top_p": 0.85,
                "max_retries": 0,
            }
        }

        if task_type not in model_config:
            raise ValueError(f"Unsupported task_type: {task_type}")

        cfg = model_config[task_type]

        llm = ChatCerebras(
            model=cfg["model"],
            api_key=os.getenv("CEREBRAS_API_KEY"),
            temperature=cfg["temperature"],
            top_p=cfg["top_p"],
            max_retries=cfg["max_retries"],
        )
        return llm
    except Exception as e:
        # Get the traceback as a string
        traceback_str = traceback.format_exc()
        print(traceback_str)
        # Get the line number of the exception
        line_no = traceback.extract_tb(e.__traceback__)[-1][1]
        print(f"Exception occurred on line {line_no}")
        return str(e)