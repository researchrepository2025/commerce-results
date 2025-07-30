# AI Agent Chatbot Integration Plan - 100% Local Deployment

## Executive Summary

This revised plan outlines the integration of a fully local AI agent chatbot sidebar into the Agentic Commerce Dashboard. All components run on-premises without external API calls, ensuring complete data privacy and offline functionality.

## Architecture Overview - Local Stack

### Recommended Stack (Local-First, July 2025)

1. **LLM**: Ollama with Llama 3.1 70B or Mixtral 8x7B
2. **Agent Framework**: LangChain/LangGraph with local memory
3. **Vector Database**: ChromaDB (embedded mode)
4. **Backend**: FastAPI with WebSocket support
5. **Memory Storage**: 
   - SQLite (chat history, lightweight)
   - ChromaDB (vector embeddings, local)
   - Local file system (document storage)
6. **Dashboard**: Dash with WebSocket client integration

## Option 1: LangGraph + AG-UI Local Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LOCAL MACHINE                                 │
│                                                                      │
│  ┌─────────────────┐     ┌──────────────────┐     ┌──────────────┐ │
│  │   Dash Frontend │     │  FastAPI Backend │     │    Ollama      │ │
│  │                 │     │                  │     │                │ │
│  │  ┌───────────┐  │     │  ┌────────────┐ │     │  ┌──────────┐ │ │
│  │  │ Dashboard │  │◄────┤  │   AG-UI    │ │◄────┤  │ Llama 3.1│ │ │
│  │  │   Views   │  │     │  │  Protocol  │ │     │  │   70B    │ │ │
│  │  └───────────┘  │     │  └────────────┘ │     │  └──────────┘ │ │
│  │                 │     │                  │     │                │ │
│  │  ┌───────────┐  │     │  ┌────────────┐ │     │  ┌──────────┐ │ │
│  │  │  AG-UI    │  │     │  │ LangGraph  │ │     │  │ LangMem  │ │ │
│  │  │  Client   │  │◄────┤  │   Agent    │ │◄────┤  │  Local   │ │ │
│  │  └───────────┘  │     │  └────────────┘ │     │  └──────────┘ │ │
│  └─────────────────┘     └──────────────────┘     └──────────────┘ │
│           │                       │                        │         │
│           └───────────────────────┴────────────────────────┘        │
│                     WebSocket + AG-UI Protocol                       │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Local Storage                              │  │
│  │  ┌─────────┐  ┌──────────────┐  ┌─────────────────────────┐ │  │
│  │  │ SQLite  │  │  ChromaDB    │  │   File System           │ │  │
│  │  │  (.db)  │  │  (./chroma)  │  │  (./agent_memory)       │ │  │
│  │  └─────────┘  └──────────────┘  └─────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Local LLM Options

### 1. Ollama (Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull recommended models
ollama pull llama3.1:70b          # Best performance, 40GB RAM required
ollama pull mixtral:8x7b          # Good balance, 26GB RAM required
ollama pull llama3.1:8b           # Lightweight option, 8GB RAM required
ollama pull phi3:medium           # Very lightweight, 4GB RAM required
```

### 2. llama.cpp with GGUF models
```python
from llama_cpp import Llama

# Initialize local model
llm = Llama(
    model_path="./models/llama-3.1-70b-instruct.Q4_K_M.gguf",
    n_ctx=8192,  # Context window
    n_gpu_layers=35,  # GPU acceleration
    n_threads=8
)
```

### 3. vLLM for production deployments
```python
from vllm import LLM, SamplingParams

# High-performance local inference
llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    tensor_parallel_size=2,  # Multi-GPU support
    gpu_memory_utilization=0.9
)
```

## Local Memory System

### 1. SQLite for Chat History
```python
import sqlite3
from datetime import datetime

class LocalChatMemory:
    def __init__(self, db_path="./agent_memory/chat_history.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                metadata TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP,
                tool_calls TEXT,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
            )
        """)
```

### 2. ChromaDB Embedded Mode
```python
import chromadb
from chromadb.config import Settings

# Local ChromaDB instance
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./agent_memory/chroma",
    anonymized_telemetry=False
))

# Create collections for different memory types
episodic_memory = chroma_client.create_collection("episodic_memory")
semantic_memory = chroma_client.create_collection("semantic_memory")
procedural_memory = chroma_client.create_collection("procedural_memory")
```

### 3. Local File System for Documents
```python
import json
import pickle
from pathlib import Path

class LocalMemoryStore:
    def __init__(self, base_path="./agent_memory"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.base_path / "sessions").mkdir(exist_ok=True)
        (self.base_path / "learned_patterns").mkdir(exist_ok=True)
        (self.base_path / "user_preferences").mkdir(exist_ok=True)
    
    def save_session(self, session_id, data):
        path = self.base_path / "sessions" / f"{session_id}.json"
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_learned_pattern(self, pattern_name, pattern_data):
        path = self.base_path / "learned_patterns" / f"{pattern_name}.pkl"
        with open(path, 'wb') as f:
            pickle.dump(pattern_data, f)
```

## Local Agent Implementation with LangGraph + AG-UI

### 1. LangGraph with Ollama and Local Memory
```python
from langchain_community.llms import Ollama
from langchain.memory import ConversationSummaryBufferMemory
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

# Initialize local LLM
llm = Ollama(
    model="llama3.1:70b",
    temperature=0.7,
    num_ctx=8192,
    num_gpu=1,
    repeat_penalty=1.1
)

# Local embeddings
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"
)

# Local LangMem implementation
class LocalLangMem:
    def __init__(self, base_path="./agent_memory"):
        self.procedural = Chroma(
            persist_directory=f"{base_path}/procedural",
            embedding_function=embeddings,
            collection_name="procedural_memory"
        )
        self.episodic = Chroma(
            persist_directory=f"{base_path}/episodic",
            embedding_function=embeddings,
            collection_name="episodic_memory"
        )
        self.semantic = Chroma(
            persist_directory=f"{base_path}/semantic",
            embedding_function=embeddings,
            collection_name="semantic_memory"
        )

# State definition for LangGraph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    memory_context: dict
    ui_updates: list

# Custom tools for dashboard
from langchain.tools import tool

@tool
def update_market_projection(segment: str, parameter: str, value: float) -> dict:
    """Update market projection parameters for a specific segment."""
    # Implementation to update dashboard
    return {
        "status": "updated",
        "segment": segment,
        "parameter": parameter,
        "value": value,
        "ui_update": {
            "component": "projection-chart",
            "action": "update",
            "data": {segment: {parameter: value}}
        }
    }

@tool
def analyze_segment(segment: str) -> dict:
    """Analyze a specific market segment and return insights."""
    # Implementation to analyze segment
    return {
        "segment": segment,
        "insights": "Analysis results...",
        "ui_update": {
            "component": "segment-analysis",
            "action": "display",
            "data": {"segment": segment, "analysis": "..."}
        }
    }

@tool
def search_memory(query: str, memory_type: str = "all") -> list:
    """Search agent's memory for relevant information."""
    memory = LocalLangMem()
    results = []
    
    if memory_type in ["all", "semantic"]:
        results.extend(memory.semantic.similarity_search(query, k=3))
    if memory_type in ["all", "episodic"]:
        results.extend(memory.episodic.similarity_search(query, k=3))
    if memory_type in ["all", "procedural"]:
        results.extend(memory.procedural.similarity_search(query, k=2))
    
    return results

tools = [update_market_projection, analyze_segment, search_memory]
tool_executor = ToolExecutor(tools)

# Create LangGraph workflow
def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Define nodes
    def agent_node(state):
        # Get memory context
        memory = LocalLangMem()
        last_message = state["messages"][-1].content if state["messages"] else ""
        memory_results = search_memory.func(last_message)
        
        # Call LLM with context
        response = llm.invoke(
            state["messages"] + 
            [{"role": "system", "content": f"Memory context: {memory_results}"}]
        )
        
        # Parse for tool calls
        ui_updates = []
        if "update_market_projection" in response:
            # Extract and execute tool calls
            tool_result = tool_executor.invoke({"tool": "update_market_projection", "args": {...}})
            if "ui_update" in tool_result:
                ui_updates.append(tool_result["ui_update"])
        
        return {
            "messages": [response],
            "ui_updates": ui_updates
        }
    
    def tool_node(state):
        # Execute tools and collect UI updates
        ui_updates = []
        for tool_call in state.get("tool_calls", []):
            result = tool_executor.invoke(tool_call)
            if "ui_update" in result:
                ui_updates.append(result["ui_update"])
        
        return {"ui_updates": ui_updates}
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Add edges
    workflow.add_edge("agent", "tools")
    workflow.add_edge("tools", "agent")
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Compile with checkpointer for conversation persistence
    checkpointer = SqliteSaver.from_conn_string("./agent_memory/checkpoints.db")
    return workflow.compile(checkpointer=checkpointer)

# Create the compiled graph
agent_graph = create_agent_graph()
```

### 2. Custom Memory Management
```python
class LocalAgentMemory:
    def __init__(self, base_path="./agent_memory"):
        self.sqlite_path = f"{base_path}/chat.db"
        self.chroma_path = f"{base_path}/chroma"
        self.patterns_path = f"{base_path}/patterns"
        
        # Initialize components
        self.chat_db = sqlite3.connect(self.sqlite_path)
        self.vector_db = chromadb.PersistentClient(path=self.chroma_path)
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        # Memory collections
        self.episodic = self.vector_db.get_or_create_collection("episodic")
        self.semantic = self.vector_db.get_or_create_collection("semantic")
        self.procedural = self.vector_db.get_or_create_collection("procedural")
    
    def remember_interaction(self, user_input, agent_response, metadata=None):
        # Store in SQLite
        self.chat_db.execute("""
            INSERT INTO interactions (user_input, agent_response, metadata, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_input, agent_response, json.dumps(metadata), datetime.now()))
        
        # Store embeddings in ChromaDB
        embedding = self.embeddings.embed_query(f"{user_input} {agent_response}")
        self.episodic.add(
            embeddings=[embedding],
            documents=[agent_response],
            metadatas=[{"user_input": user_input, "timestamp": str(datetime.now())}]
        )
    
    def learn_pattern(self, pattern_type, pattern_data):
        # Store learned patterns locally
        pattern_path = f"{self.patterns_path}/{pattern_type}.json"
        with open(pattern_path, 'w') as f:
            json.dump(pattern_data, f)
        
        # Add to procedural memory
        self.procedural.add(
            embeddings=[self.embeddings.embed_query(str(pattern_data))],
            documents=[json.dumps(pattern_data)],
            metadatas=[{"type": pattern_type, "learned_at": str(datetime.now())}]
        )
```

## AG-UI Protocol Implementation (Local)

```python
from fastapi import FastAPI, WebSocket
from typing import Dict, Any, Optional
import asyncio
import json
import uuid
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()

# AG-UI Protocol Models
class AGUIMessage(BaseModel):
    id: str
    type: str  # 'text', 'tool_call', 'ui_update', 'error'
    timestamp: str
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}

class UIUpdate(BaseModel):
    component: str
    action: str  # 'update', 'refresh', 'append', 'replace'
    data: Any
    transition: str = 'smooth'

# AG-UI Protocol Handler
class LocalAGUIHandler:
    def __init__(self):
        self.agent_graph = create_agent_graph()
        self.memory = LocalLangMem()
        self.active_connections: Dict[str, WebSocket] = {}
        self.conversation_threads: Dict[str, str] = {}
    
    async def handle_message(self, message: AGUIMessage, websocket: WebSocket, session_id: str):
        # Get or create conversation thread
        thread_id = self.conversation_threads.get(session_id, str(uuid.uuid4()))
        self.conversation_threads[session_id] = thread_id
        
        # Process with LangGraph agent
        config = {"configurable": {"thread_id": thread_id}}
        
        # Create user message
        user_message = {
            "messages": [{"role": "user", "content": message.content.get("text", "")}]
        }
        
        # Stream response
        ui_updates = []
        response_text = ""
        
        async for event in self.agent_graph.astream(user_message, config):
            if "agent" in event:
                # Extract agent response
                agent_output = event["agent"]
                if "messages" in agent_output:
                    response_text = agent_output["messages"][-1].content
                
                # Collect UI updates
                if "ui_updates" in agent_output:
                    ui_updates.extend(agent_output["ui_updates"])
        
        # Send AG-UI formatted response
        response_message = AGUIMessage(
            id=str(uuid.uuid4()),
            type="text",
            timestamp=datetime.utcnow().isoformat(),
            content={
                "text": response_text,
                "uiUpdates": ui_updates
            },
            metadata={"thread_id": thread_id}
        )
        
        await websocket.send_json(response_message.dict())
        
        # Send UI updates separately
        for update in ui_updates:
            update_message = AGUIMessage(
                id=str(uuid.uuid4()),
                type="ui_update",
                timestamp=datetime.utcnow().isoformat(),
                content=update
            )
            await websocket.send_json(update_message.dict())
        
        # Store in memory
        self.memory.episodic.add_texts(
            texts=[response_text],
            metadatas=[{
                "user_input": message.content.get("text", ""),
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "ui_updates": json.dumps(ui_updates)
            }]
        )

@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    handler = LocalAGUIHandler()
    handler.active_connections[session_id] = websocket
    
    try:
        # Send welcome message
        welcome = AGUIMessage(
            id=str(uuid.uuid4()),
            type="text",
            timestamp=datetime.utcnow().isoformat(),
            content={
                "text": "Hello! I'm your AI market analysis assistant. I can help you update projections, analyze segments, and answer questions about the agentic commerce market."
            }
        )
        await websocket.send_json(welcome.dict())
        
        # Handle messages
        while True:
            data = await websocket.receive_text()
            message = AGUIMessage(**json.loads(data))
            await handler.handle_message(message, websocket, session_id)
            
    except Exception as e:
        error_message = AGUIMessage(
            id=str(uuid.uuid4()),
            type="error",
            timestamp=datetime.utcnow().isoformat(),
            content={"error": str(e)}
        )
        await websocket.send_json(error_message.dict())
    finally:
        del handler.active_connections[session_id]
        await websocket.close()

# Dashboard update endpoint
@app.post("/api/dashboard/update")
async def update_dashboard(update: UIUpdate):
    """Endpoint for programmatic dashboard updates"""
    # Broadcast to all connected clients
    handler = LocalAGUIHandler()
    update_message = AGUIMessage(
        id=str(uuid.uuid4()),
        type="ui_update",
        timestamp=datetime.utcnow().isoformat(),
        content=update.dict()
    )
    
    for websocket in handler.active_connections.values():
        await websocket.send_json(update_message.dict())
    
    return {"status": "broadcasted", "connections": len(handler.active_connections)}
```

## Frontend Integration (Dash)

```python
# dash_chat_sidebar.py
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import websocket
import json
import threading

class ChatSidebar:
    def __init__(self, ws_url="ws://localhost:8000/ws/agent"):
        self.ws_url = ws_url
        self.ws = None
        self.messages = []
        
    def create_layout(self):
        return dbc.Offcanvas(
            [
                html.Div([
                    html.H4("AI Assistant", className="mb-3"),
                    html.Div(id="chat-messages", style={
                        "height": "60vh",
                        "overflowY": "auto",
                        "border": "1px solid #ddd",
                        "borderRadius": "5px",
                        "padding": "10px",
                        "marginBottom": "10px"
                    }),
                    dbc.InputGroup([
                        dbc.Input(
                            id="chat-input",
                            placeholder="Ask about market projections...",
                            type="text"
                        ),
                        dbc.Button("Send", id="send-button", color="primary")
                    ])
                ])
            ],
            id="chat-sidebar",
            title="AI Market Assistant",
            placement="end",
            is_open=False,
            style={"width": "400px"}
        )
```

## System Requirements

### Minimum Requirements (8B models)
- CPU: 8-core modern processor
- RAM: 16GB
- Storage: 50GB SSD
- GPU: Optional (8GB VRAM for acceleration)

### Recommended Requirements (70B models)
- CPU: 16-core processor
- RAM: 64GB
- Storage: 200GB NVMe SSD
- GPU: NVIDIA RTX 4090 or A6000 (24GB+ VRAM)

### Production Requirements
- CPU: Dual Xeon or EPYC processors
- RAM: 128GB+
- Storage: 1TB NVMe SSD
- GPU: 2x NVIDIA A100 (80GB) for parallel inference

## Performance Optimization

### 1. Model Quantization
```python
# Use quantized models for better performance
model_configs = {
    "fast": "llama3.1:8b-instruct-q4_0",      # 4-bit quantization
    "balanced": "mixtral:8x7b-instruct-q5_K_M", # 5-bit quantization
    "quality": "llama3.1:70b-instruct-q6_K"    # 6-bit quantization
}
```

### 2. Caching Strategy
```python
from functools import lru_cache
import hashlib

class LocalCache:
    def __init__(self, cache_dir="./agent_memory/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    @lru_cache(maxsize=1000)
    def get_cached_response(self, query_hash):
        cache_file = self.cache_dir / f"{query_hash}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None
    
    def cache_response(self, query, response):
        query_hash = hashlib.md5(query.encode()).hexdigest()
        cache_file = self.cache_dir / f"{query_hash}.json"
        with open(cache_file, 'w') as f:
            json.dump({
                "query": query,
                "response": response,
                "timestamp": str(datetime.now())
            }, f)
```

### 3. Batch Processing
```python
# Process multiple requests efficiently
class BatchedLocalLLM:
    def __init__(self, model_name="llama3.1:70b"):
        self.llm = Ollama(model=model_name, num_ctx=8192)
        self.batch_queue = []
        self.batch_size = 4
        
    async def process_batch(self):
        if len(self.batch_queue) >= self.batch_size:
            batch = self.batch_queue[:self.batch_size]
            self.batch_queue = self.batch_queue[self.batch_size:]
            
            # Process in parallel using async
            tasks = [self.llm.ainvoke(req) for req in batch]
            responses = await asyncio.gather(*tasks)
            return responses
```

## Privacy and Security

### 1. Data Isolation
```python
# Ensure complete data isolation
class SecureLocalAgent:
    def __init__(self):
        # Disable all telemetry
        os.environ['ANONYMIZED_TELEMETRY'] = 'False'
        os.environ['OLLAMA_HOST'] = 'localhost:11434'
        
        # Block external requests
        self.allowed_hosts = ['localhost', '127.0.0.1']
    
    def validate_local_only(self, url):
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.hostname not in self.allowed_hosts:
            raise ValueError(f"External request blocked: {url}")
```

### 2. Memory Encryption
```python
from cryptography.fernet import Fernet

class EncryptedMemory:
    def __init__(self, key_path="./agent_memory/.key"):
        self.key = self._load_or_create_key(key_path)
        self.cipher = Fernet(self.key)
    
    def encrypt_data(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode())
    
    def decrypt_data(self, encrypted: bytes) -> str:
        return self.cipher.decrypt(encrypted).decode()
```

## Advantages of Local Deployment

1. **Complete Privacy**: No data leaves your infrastructure
2. **No API Costs**: One-time hardware investment
3. **Offline Operation**: Works without internet
4. **Low Latency**: No network round trips
5. **Customization**: Fine-tune models on your data
6. **Compliance**: Meets strict data residency requirements

## Disadvantages and Mitigation

| Challenge | Mitigation |
|-----------|------------|
| Lower model quality vs GPT-4 | Use largest local models (70B+), fine-tune on domain data |
| Higher hardware costs | Start with smaller models, scale as needed |
| Maintenance overhead | Use containerization, automated updates |
| Limited context window | Implement intelligent chunking and summarization |
| Slower inference | Use GPU acceleration, model quantization |

## Implementation Timeline

### Phase 1: Core Setup (Week 1)
- Install Ollama and download models
- Set up SQLite and ChromaDB
- Create basic FastAPI backend
- Implement WebSocket handler

### Phase 2: Agent Development (Week 2)
- Build LangChain agent with local LLM
- Implement memory system
- Create dashboard update tools
- Add basic chat interface

### Phase 3: Integration (Week 3)
- Integrate chat sidebar with Dash
- Connect WebSocket communication
- Implement real-time updates
- Add memory persistence

### Phase 4: Optimization (Week 4)
- Implement caching layer
- Add batch processing
- Optimize model inference
- Performance testing

## Cost Comparison

### Local Setup (One-time)
- **Hardware**: $5,000-15,000 (depending on GPU)
- **Electricity**: ~$100/month
- **Maintenance**: 1-2 hours/week
- **Total Year 1**: $6,200-16,200

### Cloud API (Original Plan)
- **Monthly**: $1,150-2,150
- **Total Year 1**: $13,800-25,800

**Break-even**: 6-12 months

## Conclusion

The 100% local deployment is entirely feasible and offers significant advantages for privacy-conscious deployments. While it requires higher upfront investment and some quality trade-offs compared to GPT-4, modern open models like Llama 3.1 70B provide excellent performance for most use cases. The architecture remains fundamentally the same, just replacing cloud services with local equivalents.