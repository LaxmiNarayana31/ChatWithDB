import os
import traceback

from dotenv import load_dotenv
from langchain_cerebras.chat_models import ChatCerebras
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

load_dotenv(verbose=True)

def get_llm_client():
    try:
        llm = ChatCerebras(
            model="llama3.1-8b",
            api_key=os.getenv("CEREBRAS_API_KEY"),
            temperature=0.8,
            top_p=0.85,
            max_retries=0,
            # streaming=True
        )
        # llm = ChatGoogleGenerativeAI(
        #         model = "gemini-2.5-pro" , 
        #         google_api_key = os.getenv("GOOGLE_API_KEY"), 
        #         temperature = 0.8, 
        #         top_p = 0.85, 
        #         max_retries = 0
        #     )
        return llm
    except Exception as e:
        # Get the traceback as a string
        traceback_str = traceback.format_exc()
        print(traceback_str)
        # Get the line number of the exception
        line_no = traceback.extract_tb(e.__traceback__)[-1][1]
        print(f"Exception occurred on line {line_no}")
        return str(e)