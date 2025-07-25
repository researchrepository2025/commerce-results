"""
LangGraph agent with local LLM and memory management
"""
import os
import json
from typing import TypedDict, Annotated, Sequence, Dict, Any, List
import operator
from datetime import datetime
from pathlib import Path

from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langgraph.checkpoint.sqlite import SqliteSaver

from models import UIUpdate, DashboardUpdate


# Initialize local LLM
llm = Ollama(
    model="gemma3n:e2b",  # Using the best available model (4.5B)
    temperature=0.7,
    num_ctx=4096,  # Adjusted for gemma3n
    num_gpu=1,
    repeat_penalty=1.1,
    base_url="http://localhost:11434"
)

# Local embeddings
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"
)


class LocalLangMem:
    """Local implementation of LangMem-style memory system"""
    
    def __init__(self, base_path: str = "./agent_memory"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Initialize three types of memory
        self.procedural = Chroma(
            persist_directory=str(self.base_path / "procedural"),
            embedding_function=embeddings,
            collection_name="procedural_memory"
        )
        
        self.episodic = Chroma(
            persist_directory=str(self.base_path / "episodic"),
            embedding_function=embeddings,
            collection_name="episodic_memory"
        )
        
        self.semantic = Chroma(
            persist_directory=str(self.base_path / "semantic"),
            embedding_function=embeddings,
            collection_name="semantic_memory"
        )
    
    def store_interaction(self, user_input: str, agent_response: str, metadata: Dict[str, Any] = None):
        """Store interaction in episodic memory"""
        self.episodic.add_texts(
            texts=[f"User: {user_input}\nAssistant: {agent_response}"],
            metadatas=[{
                "timestamp": datetime.utcnow().isoformat(),
                "user_input": user_input,
                "agent_response": agent_response,
                **(metadata or {})
            }]
        )
    
    def learn_pattern(self, pattern_name: str, pattern_data: Dict[str, Any]):
        """Store learned patterns in procedural memory"""
        self.procedural.add_texts(
            texts=[json.dumps(pattern_data)],
            metadatas=[{
                "pattern_name": pattern_name,
                "learned_at": datetime.utcnow().isoformat(),
                "type": "learned_behavior"
            }]
        )
    
    def store_fact(self, fact: str, source: str = "user", confidence: float = 1.0):
        """Store facts in semantic memory"""
        self.semantic.add_texts(
            texts=[fact],
            metadatas=[{
                "source": source,
                "confidence": confidence,
                "stored_at": datetime.utcnow().isoformat()
            }]
        )
    
    def search_all(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search across all memory types"""
        results = []
        
        # Search each memory type
        for memory_type, store in [
            ("semantic", self.semantic),
            ("episodic", self.episodic),
            ("procedural", self.procedural)
        ]:
            docs = store.similarity_search_with_score(query, k=k//3 + 1)
            for doc, score in docs:
                results.append({
                    "type": memory_type,
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": 1 - score  # Convert distance to similarity
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:k]


# State definition for LangGraph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    memory_context: List[Dict[str, Any]]
    ui_updates: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]


# Tool definitions
@tool
def update_market_projection(segment: str, parameter: str, value: float, year: int = 2025) -> Dict[str, Any]:
    """Update market projection parameters for a specific segment.
    
    Args:
        segment: Market segment (consumer, business, government)
        parameter: Parameter to update (adoption_rate, spending, etc.)
        value: New value for the parameter
        year: Target year (default: 2025)
    
    Returns:
        Update status and UI update instruction
    """
    # Validate inputs
    valid_segments = ['consumer', 'business', 'government']
    if segment not in valid_segments:
        return {"error": f"Invalid segment. Must be one of: {valid_segments}"}
    
    # Create UI update
    ui_update = UIUpdate(
        component=f"{segment}-projection",
        action="update",
        data={
            "segment": segment,
            "parameter": parameter,
            "value": value,
            "year": year
        }
    )
    
    return {
        "status": "success",
        "message": f"Updated {segment} {parameter} to {value} for year {year}",
        "ui_update": ui_update.dict()
    }


@tool
def analyze_market_segment(segment: str, metrics: List[str] = None) -> Dict[str, Any]:
    """Analyze a specific market segment and return insights.
    
    Args:
        segment: Market segment to analyze
        metrics: Optional list of specific metrics to analyze
    
    Returns:
        Analysis results and UI update
    """
    # Simulated analysis (in production, this would query actual data)
    analysis = {
        "segment": segment,
        "current_value": "Analysis based on current dashboard data",
        "trends": "Positive growth trajectory",
        "key_insights": [
            f"{segment} shows strong adoption potential",
            "Growth rate exceeds market average",
            "Risk factors are well-managed"
        ]
    }
    
    ui_update = UIUpdate(
        component="analysis-panel",
        action="display",
        data=analysis
    )
    
    return {
        "analysis": analysis,
        "ui_update": ui_update.dict()
    }


@tool
def search_memory(query: str, memory_type: str = "all") -> List[Dict[str, Any]]:
    """Search agent's memory for relevant information.
    
    Args:
        query: Search query
        memory_type: Type of memory to search (all, semantic, episodic, procedural)
    
    Returns:
        Relevant memory entries
    """
    memory = LocalLangMem()
    
    if memory_type == "all":
        results = memory.search_all(query, k=5)
    else:
        store_map = {
            "semantic": memory.semantic,
            "episodic": memory.episodic,
            "procedural": memory.procedural
        }
        if memory_type in store_map:
            docs = store_map[memory_type].similarity_search(query, k=5)
            results = [
                {
                    "type": memory_type,
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in docs
            ]
        else:
            results = []
    
    return results


@tool
def save_market_scenario(name: str, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Save a market scenario for future reference.
    
    Args:
        name: Scenario name
        description: Scenario description
        parameters: Current dashboard parameters
    
    Returns:
        Save status
    """
    memory = LocalLangMem()
    
    # Store in semantic memory as a fact
    fact = f"Market Scenario '{name}': {description}"
    memory.store_fact(fact, source="user_scenario", confidence=1.0)
    
    # Store detailed parameters in procedural memory
    memory.learn_pattern(
        pattern_name=f"scenario_{name}",
        pattern_data={
            "name": name,
            "description": description,
            "parameters": parameters,
            "created_at": datetime.utcnow().isoformat()
        }
    )
    
    return {
        "status": "success",
        "message": f"Saved scenario '{name}' to memory"
    }


# Tool executor
tools = [
    update_market_projection,
    analyze_market_segment,
    search_memory,
    save_market_scenario
]
tool_executor = ToolExecutor(tools)


def create_agent_graph():
    """Create the LangGraph workflow for the agent"""
    workflow = StateGraph(AgentState)
    
    # Initialize memory
    memory = LocalLangMem()
    
    def agent_node(state: AgentState) -> Dict[str, Any]:
        """Main agent logic node"""
        # Get the last user message
        messages = state.get("messages", [])
        if not messages:
            return {"messages": []}
        
        last_message = messages[-1].content
        
        # Search memory for context
        memory_results = memory.search_all(last_message, k=3)
        
        # Build context prompt
        context = "\n".join([
            f"[{r['type']}] {r['content'][:200]}..."
            for r in memory_results
        ])
        
        # Create system prompt with memory context
        system_prompt = f"""You are an AI assistant for the Agentic Commerce Market Analysis Dashboard.
You help users understand market projections, update parameters, and analyze trends.

Available tools:
- update_market_projection: Update dashboard parameters
- analyze_market_segment: Analyze specific market segments
- search_memory: Search your memory for information
- save_market_scenario: Save current scenario

Recent memory context:
{context}

Be helpful, accurate, and proactive in suggesting analyses or updates based on user queries."""
        
        # Format messages for Ollama
        formatted_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted_messages.append({"role": "assistant", "content": msg.content})
        
        # Get LLM response
        response = llm.invoke(formatted_messages)
        
        # Parse response for tool calls
        tool_calls = []
        ui_updates = []
        
        # Simple tool detection (in production, use more sophisticated parsing)
        response_lower = response.lower()
        if "update" in response_lower and "projection" in response_lower:
            # Extract parameters from response (simplified)
            tool_calls.append({
                "tool": "update_market_projection",
                "args": {
                    "segment": "consumer",  # Would parse from response
                    "parameter": "adoption_rate",
                    "value": 0.3
                }
            })
        
        # Store interaction in memory
        memory.store_interaction(
            user_input=last_message,
            agent_response=response,
            metadata={
                "tool_calls": tool_calls,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return {
            "messages": [AIMessage(content=response)],
            "memory_context": memory_results,
            "tool_calls": tool_calls,
            "ui_updates": ui_updates
        }
    
    def tool_node(state: AgentState) -> Dict[str, Any]:
        """Execute tools and collect UI updates"""
        ui_updates = []
        messages = []
        
        for tool_call in state.get("tool_calls", []):
            tool_name = tool_call["tool"]
            tool_args = tool_call.get("args", {})
            
            # Find and execute tool
            tool_func = None
            for t in tools:
                if t.name == tool_name:
                    tool_func = t
                    break
            
            if tool_func:
                result = tool_func.func(**tool_args)
                
                # Extract UI updates
                if "ui_update" in result:
                    ui_updates.append(result["ui_update"])
                
                # Add tool result to messages
                messages.append(AIMessage(
                    content=f"Tool '{tool_name}' executed: {result.get('message', 'Success')}"
                ))
        
        return {
            "messages": messages,
            "ui_updates": ui_updates
        }
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Define edges
    def should_use_tools(state: AgentState) -> str:
        """Determine if tools should be called"""
        if state.get("tool_calls"):
            return "tools"
        return END
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_use_tools,
        {
            "tools": "tools",
            END: END
        }
    )
    workflow.add_edge("tools", END)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Compile with checkpointer for conversation persistence
    checkpointer = SqliteSaver.from_conn_string("./agent_memory/checkpoints.db")
    return workflow.compile(checkpointer=checkpointer)


# Create and export the compiled graph
agent_graph = create_agent_graph()