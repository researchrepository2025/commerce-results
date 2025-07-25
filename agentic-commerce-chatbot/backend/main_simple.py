"""
Simplified FastAPI backend for testing
"""
import os
import json
import asyncio
from typing import Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from models import AGUIMessage
from ollama import Client


# Simple Ollama client
ollama_client = Client(host='http://localhost:11434')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("Starting Agentic Commerce Chatbot Backend...")
    
    # Check if Ollama is running
    try:
        models = ollama_client.list()
        if isinstance(models, dict) and 'models' in models:
            model_names = [m['name'] for m in models['models']]
        else:
            model_names = ["gemma3n:e2b"]  # Default to our known model
        print(f"✓ Ollama is running with models: {model_names}")
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
    
    yield
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
    allow_origins=["*"],  # Allow all origins for testing
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


@app.post("/api/chat")
async def chat_endpoint(request: dict):
    """Simple HTTP endpoint for chat"""
    message = request.get("message", "")
    
    try:
        # Call Ollama directly
        response = ollama_client.chat(
            model='gemma3n:e2b',
            messages=[
                {
                    'role': 'system',
                    'content': """You are an AI assistant for the Agentic Commerce Market Analysis Dashboard.
You help users understand market projections, update parameters, and analyze trends.
Be helpful, accurate, and concise in your responses."""
                },
                {
                    'role': 'user',
                    'content': message
                }
            ]
        )
        
        return {"response": response['message']['content']}
        
    except Exception as e:
        return {"response": f"I encountered an error: {str(e)}. Please check if Ollama is running."}


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "components": {
            "fastapi": "running",
            "websocket": "ready"
        }
    }
    
    # Check Ollama
    try:
        models = ollama_client.list()
        health_status["components"]["ollama"] = "running"
        if isinstance(models, dict) and 'models' in models:
            health_status["models"] = [m['name'] for m in models['models']]
        else:
            health_status["models"] = ["gemma3n:e2b"]
    except:
        health_status["components"]["ollama"] = "offline"
        health_status["status"] = "degraded"
    
    return health_status


@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for AG-UI protocol"""
    import uuid
    session_id = str(uuid.uuid4())
    
    await websocket.accept()
    
    try:
        # Send welcome message
        welcome_message = AGUIMessage(
            type="text",
            content={
                "text": "Hello! I'm your AI market analysis assistant. I can help you:\n"
                        "• Update market projections for any segment\n"
                        "• Analyze trends and provide insights\n"
                        "• Answer questions about the agentic commerce market\n\n"
                        "What would you like to explore?",
                "role": "assistant"
            },
            metadata={"session_id": session_id}
        )
        await websocket.send_json(welcome_message.dict())
        
        # Message handling loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Extract user text
            if isinstance(message_data, dict) and "content" in message_data:
                user_text = message_data["content"].get("text", "")
            else:
                user_text = str(message_data)
            
            # Send thinking status
            thinking_message = AGUIMessage(
                type="status",
                content={"status": "thinking", "text": "Processing your request..."}
            )
            await websocket.send_json(thinking_message.dict())
            
            try:
                # Call Ollama
                response = ollama_client.chat(
                    model='gemma3n:e2b',  # Using the best available model
                    messages=[
                        {
                            'role': 'system',
                            'content': """You are an AI assistant for the Agentic Commerce Market Analysis Dashboard.
You help users understand market projections, update parameters, and analyze trends.
Be helpful, accurate, and concise in your responses."""
                        },
                        {
                            'role': 'user',
                            'content': user_text
                        }
                    ]
                )
                
                # Extract response text
                response_text = response['message']['content']
                
                # Send agent response
                response_message = AGUIMessage(
                    type="text",
                    content={
                        "text": response_text,
                        "role": "assistant"
                    },
                    metadata={"session_id": session_id}
                )
                await websocket.send_json(response_message.dict())
                
                # Check for dashboard updates in response
                if any(keyword in response_text.lower() for keyword in ['update', 'set', 'change']):
                    # Simple UI update example
                    update_message = AGUIMessage(
                        type="ui_update",
                        content={
                            "component": "notification",
                            "action": "display",
                            "data": {
                                "message": "To update the dashboard, use the controls in the respective tabs.",
                                "type": "info"
                            }
                        }
                    )
                    await websocket.send_json(update_message.dict())
                
            except Exception as e:
                # Send error message
                error_message = AGUIMessage(
                    type="error",
                    content={
                        "error": str(e),
                        "message": "I encountered an error. Please check if Ollama is running."
                    }
                )
                await websocket.send_json(error_message.dict())
    
    except WebSocketDisconnect:
        print(f"Client {session_id} disconnected")
    except Exception as e:
        print(f"WebSocket error for {session_id}: {e}")


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )