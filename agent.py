from typing import TypedDict
from langchain.tools import StructuredTool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from config import TAVILY_API_KEY, GROQ_API_KEY


# ==============================
# 🔍 SEARCH TOOL
# ==============================

def extract_search_results(raw_results):
    """
    Extract structured, readable text from Tavily raw results.
    """
    extracted_results = []
    for item in raw_results:
        structured_query = (
            f"URL: {item.get('url', '')}\n"
            f"Title: {item.get('title', '')}\n"
            f"Content: {item.get('content', '')}\n---\n"
        )
        extracted_results.append(structured_query)
    return '\n'.join(extracted_results)


# Initialize Tavily search tool
web_search = TavilySearchResults(
    search_depth="basic",
    max_results=3,
    tavily_api_key=TAVILY_API_KEY,
    include_raw_content=False,
    include_images=False,
    max_tokens=2000,
    include_answer=False
)


class WebSearchInput(TypedDict):
    query: str


def web_search_tool_fn(query: str) -> str:
    """
    Search agricultural information (chemicals, fertilizers, pesticides, etc.)
    Returns summarized search results.
    """
    try:
        print(f"[🌐 Searching for]: {query}")
        result = web_search.invoke({"query": query})

        # Tavily can return a string or dict
        if isinstance(result, str):
            return result

        raw_results = result.get("results", [])
        if not raw_results:
            return "No relevant results found."

        return extract_search_results(raw_results)

    except Exception as e:
        return f"[Search Error]: {str(e)}"


# Wrap the search function for LangGraph
web_search_tool = StructuredTool.from_function(
    func=web_search_tool_fn,
    name="web_search_tool",
    description="Searches for agricultural information using Tavily Search API."
)


# ==============================
# 🧠 AGENT INITIALIZATION
# ==============================

def initialize_agent():
    """
    Initialize the LangGraph ReAct agent with memory and tools.
    """
    try:
        print("[🤖 Initializing LangGraph Agent...]")
        memory = MemorySaver()
        model = ChatGroq(
            model="llama-3.1-70b-versatile",  # ✅ More stable than 120B for inference
            temperature=0.3,
            max_tokens=1500,
            api_key=GROQ_API_KEY
        )
        tools = [web_search_tool]
        agent_executor = create_react_agent(model, tools, checkpointer=memory)
        print("[✅ Agent Initialized Successfully]")
        return agent_executor
    except Exception as e:
        print(f"[❌ Agent Initialization Error]: {e}")
        return None


# ==============================
# 💬 PROMPT + QUERY PIPELINE
# ==============================

def chat_completion(user_input: str):
    """
    Build structured conversation context for the agent.
    """
    return [
        {
            "role": "system",
            "content": """
You are a helpful agricultural assistant for farmers in Pakistan. 
You explain the usage, safety, and crop compatibility of agricultural chemicals 
like pesticides, herbicides, and fertilizers.

Inputs you may receive:
- Text from OCR (e.g., label details)
- Farmer’s voice query or typed question

Your goals:
1. Identify the chemical or fertilizer.
2. Explain its purpose and safe usage.
3. Warn about hazards or misuse risks.
4. If uncertain, use web_search_tool once for reliable agricultural sources.
5. Keep your answer simple, short, and practical.
"""
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]


def run_query(input_message, agent_executor=None):
    """
    Run the agent with given input message and return the final text output.
    """
    if agent_executor is None:
        print("[⚠️ Warning]: Agent not initialized. Initializing now...")
        agent_executor = initialize_agent()

    try:
        print("[💬 Running Agent Query...]")
        config = {"configurable": {"thread_id": "farmguide-session"}}
        response_text = ""

        for step in agent_executor.stream(
            {"messages": input_message}, config, stream_mode="values"
        ):
            latest_msg = step["messages"][-1]
            role = latest_msg.get("role", "assistant")
            content = latest_msg.get("content", "")
            if role == "assistant":
                response_text = content  # capture the final answer

        print(f"[✅ Agent Response]: {response_text}")
        return response_text

    except Exception as e:
        print(f"[❌ Agent Execution Error]: {e}")
        return "Sorry, I encountered an issue while processing your query."
