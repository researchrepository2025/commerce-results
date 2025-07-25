"""
FastAPI backend with WebSocket support for AG-UI protocol
"""
import os
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from models import AGUIMessage, UIUpdate, ChatMessage, ConversationThread
from agent import agent_graph, LocalLangMem
from langchain_core.messages import HumanMessage, AIMessage


# Store active connections and conversations
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.conversation_threads: Dict[str, ConversationThread] = {}
        self.memory = LocalLangMem()
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        
        # Create or retrieve conversation thread
        if session_id not in self.conversation_threads:
            self.conversation_threads[session_id] = ConversationThread(
                session_id=session_id
            )
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: AGUIMessage):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message.dict())
    
    async def broadcast_ui_update(self, update: UIUpdate):
        """Broadcast UI update to all connected clients"""
        update_message = AGUIMessage(
            type="ui_update",
            content=update.dict()
        )
        
        # Send to all active connections
        disconnected = []
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(update_message.dict())
            except:
                disconnected.append(session_id)
        
        # Clean up disconnected clients
        for session_id in disconnected:
            self.disconnect(session_id)


# Create connection manager
manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("Starting Agentic Commerce Chatbot Backend...")
    
    # Check if Ollama is running
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                print("✓ Ollama is running")
                models = response.json().get("models", [])
                print(f"  Available models: {[m['name'] for m in models]}")
            else:
                print("✗ Ollama is not responding properly")
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("  Please start Ollama with: ollama serve")
    
    yield
    
    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Agentic Commerce AI Agent",
    description="Local AI agent for market analysis dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8050", "http://127.0.0.1:8050"],  # Dash default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Agentic Commerce AI Agent",
        "protocol": "AG-UI",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "components": {
            "fastapi": "running",
            "websocket": "ready",
            "memory": "initialized",
            "active_connections": len(manager.active_connections)
        }
    }
    
    # Check Ollama
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            health_status["components"]["ollama"] = "running" if response.status_code == 200 else "error"
    except:
        health_status["components"]["ollama"] = "offline"
        health_status["status"] = "degraded"
    
    return health_status


@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for AG-UI protocol"""
    import uuid
    session_id = str(uuid.uuid4())
    
    # Connect client
    await manager.connect(websocket, session_id)
    thread = manager.conversation_threads[session_id]
    
    try:
        # Send welcome message
        welcome_message = AGUIMessage(
            type="text",
            content={
                "text": "Hello! I'm your AI market analysis assistant. I can help you:\n"
                        "• Update market projections for any segment\n"
                        "• Analyze trends and provide insights\n"
                        "• Save and recall market scenarios\n"
                        "• Answer questions about the agentic commerce market\n\n"
                        "What would you like to explore?",
                "suggestions": [
                    "Analyze consumer segment trends",
                    "Update business adoption rates",
                    "Compare government segments",
                    "Show me growth projections"
                ]
            },
            metadata={"session_id": session_id, "thread_id": thread.thread_id}
        )
        await manager.send_message(session_id, welcome_message)
        
        # Message handling loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Parse incoming message
            if isinstance(message_data, dict) and "content" in message_data:
                user_text = message_data["content"].get("text", "")
            else:
                user_text = str(message_data)
            
            # Create AG-UI message
            user_message = AGUIMessage(
                type="text",
                content={"text": user_text},
                metadata={"role": "user", "session_id": session_id}
            )
            
            # Process with agent
            config = {"configurable": {"thread_id": thread.thread_id}}
            
            # Send thinking status
            thinking_message = AGUIMessage(
                type="status",
                content={"status": "thinking", "text": "Processing your request..."}
            )
            await manager.send_message(session_id, thinking_message)
            
            # Run agent
            ui_updates = []
            response_text = ""
            
            try:
                # Create input for agent
                agent_input = {
                    "messages": [HumanMessage(content=user_text)],
                    "memory_context": [],
                    "ui_updates": [],
                    "tool_calls": []
                }
                
                # Stream agent response
                async for event in agent_graph.astream(agent_input, config):
                    for node_name, node_output in event.items():
                        if node_name == "agent" and "messages" in node_output:
                            # Extract agent response
                            for msg in node_output["messages"]:
                                if isinstance(msg, AIMessage):
                                    response_text = msg.content
                        
                        # Collect UI updates
                        if "ui_updates" in node_output:
                            ui_updates.extend(node_output["ui_updates"])
                
                # Send agent response
                response_message = AGUIMessage(
                    type="text",
                    content={
                        "text": response_text,
                        "role": "assistant"
                    },
                    metadata={
                        "session_id": session_id,
                        "thread_id": thread.thread_id,
                        "has_ui_updates": len(ui_updates) > 0
                    }
                )
                await manager.send_message(session_id, response_message)
                
                # Send UI updates
                for update in ui_updates:
                    update_message = AGUIMessage(
                        type="ui_update",
                        content=update
                    )
                    await manager.send_message(session_id, update_message)
                    
                    # Also broadcast to all clients
                    if "component" in update:
                        await manager.broadcast_ui_update(UIUpdate(**update))
                
            except Exception as e:
                # Send error message
                error_message = AGUIMessage(
                    type="error",
                    content={
                        "error": str(e),
                        "message": "I encountered an error processing your request. Please try again."
                    }
                )
                await manager.send_message(session_id, error_message)
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        print(f"Client {session_id} disconnected")
    except Exception as e:
        print(f"WebSocket error for {session_id}: {e}")
        manager.disconnect(session_id)


@app.post("/api/dashboard/update")
async def update_dashboard(update: UIUpdate):
    """REST endpoint for programmatic dashboard updates"""
    # Validate update
    if not update.component or not update.data:
        raise HTTPException(status_code=400, detail="Invalid update parameters")
    
    # Broadcast to all connected clients
    await manager.broadcast_ui_update(update)
    
    # Store in memory as a fact
    manager.memory.store_fact(
        fact=f"Dashboard update: {update.component} {update.action} with {json.dumps(update.data)}",
        source="api",
        confidence=1.0
    )
    
    return {
        "status": "success",
        "message": f"Updated {update.component}",
        "broadcast_to": len(manager.active_connections)
    }


@app.get("/api/memory/search")
async def search_memory(query: str, memory_type: str = "all", limit: int = 5):
    """Search agent memory"""
    results = manager.memory.search_all(query, k=limit)
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }


@app.post("/api/memory/fact")
async def store_fact(fact: str, source: str = "api", confidence: float = 1.0):
    """Store a fact in semantic memory"""
    manager.memory.store_fact(fact, source, confidence)
    return {"status": "stored", "fact": fact}


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )