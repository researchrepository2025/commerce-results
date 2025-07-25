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
from tools import AVAILABLE_TOOLS, execute_tool, dashboard_state


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
    """Enhanced HTTP endpoint for chat with tool support"""
    message = request.get("message", "")
    
    try:
        # System prompt with tool instructions
        system_prompt = f"""You are an AI assistant for the Agentic Commerce Market Analysis Dashboard.
You help users understand market projections, update parameters, and analyze trends.

You have access to the following tools to interact with the dashboard:

1. update_dashboard_variable(variable_name, new_value) - Update dashboard parameters
   - Examples: gen_z_adoption_rate, retail_spending, federal_readiness
   
2. get_dashboard_variable(variable_name) - Get current value of a variable

3. list_dashboard_variables() - List all available variables

4. calculate_market_projection(segment, year) - Calculate projections

When users ask to:
- "Set Gen Z adoption to 30%" → use update_dashboard_variable("gen_z_adoption_rate", 30.0)
- "What's the current retail spending?" → use get_dashboard_variable("retail_spending")
- "Show me all variables" → use list_dashboard_variables()
- "Calculate 2026 consumer projection" → use calculate_market_projection("consumer", 2026)

IMPORTANT: If you need to use a tool, respond with a JSON object using EXACTLY these formats:

For updating variables:
{{"tool_call": "update_dashboard_variable", "arguments": {{"variable_name": "gen_z_adoption_rate", "new_value": 35.0}}}}

For getting variables:
{{"tool_call": "get_dashboard_variable", "arguments": {{"variable_name": "gen_z_adoption_rate"}}}}

For listing all variables:
{{"tool_call": "list_dashboard_variables", "arguments": {{}}}}

For market projections:
{{"tool_call": "calculate_market_projection", "arguments": {{"segment": "consumer", "year": 2025}}}}

Available variables include:
- Generation rates: gen_z_adoption_rate, millennials_adoption_rate, gen_x_adoption_rate, baby_boomers_adoption_rate  
- Generation spending: gen_z_spending_per_person, millennials_spending_per_person, etc.
- Business rates: retail_adoption_rate, healthcare_adoption_rate, finance_adoption_rate, etc.
- Business spending: retail_spending, healthcare_spending, finance_spending, etc.
- Government: federal_readiness, state_readiness, local_readiness, federal_spending, etc.
- Growth rates: consumer_growth_rate, business_growth_rate, government_growth_rate
- Fees: payment_rate, ai_rate, ad_rate, data_rate

Be helpful and proactive in suggesting dashboard modifications!"""

        # Call Ollama
        response = ollama_client.chat(
            model='gemma3n:e2b',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ]
        )
        
        response_text = response['message']['content']
        
        # Check if response contains a tool call (handle various formats)
        tool_request = None
        
        # Try to extract JSON from markdown code blocks
        if '```json' in response_text:
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    tool_request = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
        
        # Try to parse if it starts with {
        elif response_text.strip().startswith('{') and 'tool_call' in response_text:
            try:
                tool_request = json.loads(response_text.strip())
            except json.JSONDecodeError:
                pass
        
        if tool_request and 'tool_call' in tool_request:
            try:
                tool_name = tool_request.get('tool_call')
                arguments = tool_request.get('arguments', {})
                
                # Fix common misspellings
                tool_name_fixes = {
                    'get_dashboaard_variable': 'get_dashboard_variable',
                    'update_dashboaard_variable': 'update_dashboard_variable',
                    'list_dashboaard_variables': 'list_dashboard_variables',
                    'calculate_market_projection': 'calculate_market_projection'
                }
                
                if tool_name in tool_name_fixes:
                    tool_name = tool_name_fixes[tool_name]
                
                # Execute the tool
                tool_result = execute_tool(tool_name, arguments)
                
                # Get a natural language response about the tool result
                followup_response = ollama_client.chat(
                    model='gemma3n:e2b',
                    messages=[
                        {'role': 'system', 'content': 'You are explaining the result of a dashboard operation. Be conversational and helpful.'},
                        {'role': 'user', 'content': f'I executed {tool_name} with arguments {arguments}. The result was: {tool_result}. Please explain this result in a natural, helpful way.'}
                    ]
                )
                
                return {
                    "response": followup_response['message']['content'],
                    "tool_used": tool_name,
                    "tool_result": tool_result
                }
                
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as regular response
                pass
        
        return {"response": response_text}
        
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


@app.get("/api/dashboard/state")
async def get_dashboard_state():
    """Get current dashboard state"""
    return {
        "status": "success",
        "data": dashboard_state.get_all()
    }


@app.post("/api/dashboard/update")
async def update_dashboard_state(request: dict):
    """Update dashboard variables"""
    updates = request.get("updates", {})
    results = {}
    
    for variable, value in updates.items():
        success = dashboard_state.set(variable, value)
        results[variable] = {
            "success": success,
            "new_value": value if success else None
        }
    
    return {
        "status": "success",
        "results": results
    }


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