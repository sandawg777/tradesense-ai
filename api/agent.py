import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1
)

from api.tools import (
    get_stock_price,
    get_technical_indicators,
    get_fundamental_data,
    search_trading_knowledge,
    get_market_news,
    get_sector_performance,
    screen_stocks
)

tools = [
    get_stock_price,
    get_technical_indicators,
    get_fundamental_data,
    search_trading_knowledge,
    get_market_news,
    get_sector_performance,
    screen_stocks
]

prompt = PromptTemplate.from_template("""You are an expert AI trading research assistant with deep knowledge of technical analysis, fundamental analysis, and swing trading strategies.

You have access to the following tools:
{tools}

CRITICAL RULES:
- For "hot sectors" or "what's hot" questions: ALWAYS use get_sector_performance first
- For "find stocks" or "screen for stocks": use screen_stocks with criteria
- For specific stock analysis: use get_stock_price -> get_technical_indicators -> get_fundamental_data
- For news questions: use get_market_news
- BE EFFICIENT: Don't repeat tool calls. Get the data, then provide the Final Answer
- When asked to find stocks, return SPECIFIC TICKERS with current data
- NEVER assume what's hot - always check live data

Use this format:
Question: the input question you must answer
Thought: think about what to do next
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat as needed, but be efficient)
Thought: I now have enough information to provide a comprehensive analysis
Final Answer: [Your complete structured research report with SPECIFIC tickers and data]

Previous conversation:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}""")

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=15,
    max_execution_time=120
)

store = {}


def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


agent_with_memory = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="output"
)


def analyze(question: str, session_id: str = "default") -> str:
    try:
        response = agent_with_memory.invoke(
            {"input": question},
            config={
                "configurable": {"session_id": session_id},
                "run_name": "trading_analysis",
                "tags": ["trading", "research"]
            }
        )
        return response["output"]
    except Exception as e:
        return f"Analysis error: {str(e)}"
