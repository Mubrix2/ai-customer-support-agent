# app/core/agent.py
import logging
from typing import Annotated
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

from app.config import GROQ_API_KEY, LLM_MODEL, TEMPERATURE, MAX_ITERATIONS
from app.core.tools import TOOLS
from app.core.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


# ── State definition ──────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """
    The state that travels through the graph on every turn.

    messages: the full conversation history.
    add_messages is a reducer — it appends new messages to the list
    rather than replacing it. This is how memory works in LangGraph.
    """
    messages: Annotated[list, add_messages]


# ── LLM setup ─────────────────────────────────────────────────────────────────

def get_llm():
    """Create the LLM with tools bound to it."""
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=TEMPERATURE,
    )
    # Binding tools tells the LLM what tools exist and what they do.
    # The LLM reads each tool's name, description, and argument schema
    # and can then request tool calls in its response.
    return llm.bind_tools(TOOLS)


# ── Node definitions ──────────────────────────────────────────────────────────

def llm_node(state: AgentState) -> dict:
    """
    The main LLM node.
    Prepends the system prompt and calls the LLM with the full message history.
    Returns the LLM's response to be added to state.
    """
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    llm = get_llm()
    response = llm.invoke(messages)
    logger.info(
        f"LLM response generated. "
        f"Tool calls: {len(response.tool_calls) if hasattr(response, 'tool_calls') else 0}"
    )
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """
    Conditional edge — the router.
    After the LLM responds, check if it requested any tool calls.
    If yes → go to tools node.
    If no → end the graph (return final answer to user).
    """
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        logger.info(f"Routing to tools: {[tc['name'] for tc in last_message.tool_calls]}")
        return "tools"
    return END


# ── Graph construction ────────────────────────────────────────────────────────

def build_agent():
    """
    Build and compile the LangGraph agent.
    Returns a compiled graph ready to invoke.
    """
    # MemorySaver stores conversation state in memory keyed by thread_id.
    # thread_id = session_id in our case — each user conversation is isolated.
    memory = MemorySaver()

    # Tool node — LangGraph's prebuilt ToolNode handles tool execution.
    # It receives the tool calls from the LLM, executes them, and returns results.
    tool_node = ToolNode(TOOLS)

    # Build the graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("llm", llm_node)
    graph.add_node("tools", tool_node)

    # Set entry point — every conversation starts at the LLM node
    graph.set_entry_point("llm")

    # Conditional edge after LLM — did it request tools?
    graph.add_conditional_edges(
        "llm",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    # After tools execute, always go back to LLM
    # The LLM then sees the tool results and decides what to do next
    graph.add_edge("tools", "llm")

    # Compile with memory checkpointer
    compiled = graph.compile(checkpointer=memory)
    logger.info("LangGraph agent compiled successfully")
    return compiled


# Lazy singleton — agent compiled once at startup
_agent = None


def get_agent():
    """Return the compiled agent, creating it once."""
    global _agent
    if _agent is None:
        _agent = build_agent()
        logger.info("Agent singleton initialised")
    return _agent


# ── Public interface ──────────────────────────────────────────────────────────

def chat(message: str, session_id: str) -> dict:
    """
    Send a message to the agent and get a response.
    The session_id is used as the thread_id for MemorySaver —
    this is what isolates one user's conversation from another.

    Args:
        message: The user's message
        session_id: Unique identifier for this conversation

    Returns:
        Dict with response text and metadata
    """
    agent = get_agent()

    config = {
        "configurable": {
            "thread_id": session_id,
        },
        "recursion_limit": MAX_ITERATIONS,
    }

    logger.info(f"Processing message for session '{session_id}': '{message[:60]}'")

    result = agent.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config,
    )

    # Extract the final response — last message in state
    final_message = result["messages"][-1]
    response_text = final_message.content

    # Extract tool calls made during this turn for frontend display
    tools_used = []
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tools_used.append(tc["name"])

    logger.info(
        f"Response generated for session '{session_id}'. "
        f"Tools used: {tools_used or 'none'}"
    )

    return {
        "response": response_text,
        "session_id": session_id,
        "tools_used": tools_used,
    }