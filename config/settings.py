import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def get_llm():
    """
    Initializes and returns the Gemini 2.5 Flash model instance.
    This centralized function ensures all agents use the same configuration
    by explicitly loading the required API key.
    """
    # Explicitly get the API key from the environment
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-preview-05-20",
        temperature=0.1,  # Controls the creativity of the model
        api_key=google_api_key # Pass the key directly to the model
    )
    return llm

