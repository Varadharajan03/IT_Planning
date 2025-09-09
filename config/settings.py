from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm():
    """
    Initializes and returns the Gemini 2.5 Flash model instance.
    This centralized function ensures all agents use the same configuration.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-preview-05-20",
        temperature=0.1  # Controls the creativity of the model
    )
    return llm
