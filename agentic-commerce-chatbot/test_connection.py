#!/usr/bin/env python3
"""
Test script to verify the AI chatbot backend is working
"""
import asyncio
import json
import httpx
import websockets
from datetime import datetime


async def test_health_check():
    """Test REST API health check"""
    print("🔍 Testing health check endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to backend: {e}")
            return False


async def test_websocket_connection():
    """Test WebSocket connection and basic chat"""
    print("\n🔍 Testing WebSocket connection...")
    
    try:
        async with websockets.connect("ws://localhost:8000/ws/agent") as websocket:
            print("✅ WebSocket connected")
            
            # Wait for welcome message
            welcome = await websocket.recv()
            welcome_msg = json.loads(welcome)
            print(f"✅ Received welcome: {welcome_msg.get('content', {}).get('text', '')[:100]}...")
            
            # Send test message
            test_message = {
                "type": "text",
                "content": {"text": "Hello! Can you hear me?"},
                "metadata": {"test": True}
            }
            await websocket.send(json.dumps(test_message))
            print("✅ Sent test message")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=30)
            response_msg = json.loads(response)
            print(f"✅ Received response: {response_msg.get('content', {}).get('text', '')[:100]}...")
            
            # Test tool usage
            tool_message = {
                "type": "text",
                "content": {"text": "What tools do you have available?"},
                "metadata": {"test": True}
            }
            await websocket.send(json.dumps(tool_message))
            
            response = await asyncio.wait_for(websocket.recv(), timeout=30)
            response_msg = json.loads(response)
            print(f"✅ Tool query response: {response_msg.get('content', {}).get('text', '')[:200]}...")
            
            return True
            
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response - Ollama might be slow or not running")
        return False
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False


async def test_memory_api():
    """Test memory search API"""
    print("\n🔍 Testing memory API...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Store a fact
            fact_response = await client.post(
                "http://localhost:8000/api/memory/fact",
                params={
                    "fact": "Test fact: The dashboard supports three segments",
                    "source": "test",
                    "confidence": 1.0
                }
            )
            print(f"✅ Stored fact: {fact_response.json()}")
            
            # Search memory
            search_response = await client.get(
                "http://localhost:8000/api/memory/search",
                params={"query": "dashboard segments", "limit": 5}
            )
            print(f"✅ Memory search: Found {search_response.json().get('count', 0)} results")
            
            return True
            
        except Exception as e:
            print(f"❌ Memory API test failed: {e}")
            return False


async def check_ollama():
    """Check if Ollama is running and has required models"""
    print("\n🔍 Checking Ollama status...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
                print(f"✅ Ollama is running with models: {models}")
                
                required = ['llama3.1:8b', 'nomic-embed-text']
                missing = [m for m in required if not any(m in model for model in models)]
                
                if missing:
                    print(f"⚠️  Missing required models: {missing}")
                    print(f"   Run: ollama pull {' '.join(missing)}")
                    return False
                else:
                    print("✅ All required models are available")
                    return True
            else:
                print("❌ Ollama is not responding properly")
                return False
                
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {e}")
            print("   Make sure Ollama is running: ollama serve")
            return False


async def main():
    """Run all tests"""
    print("🚀 Testing Agentic Commerce AI Chatbot")
    print("=" * 50)
    
    # Check Ollama first
    ollama_ok = await check_ollama()
    if not ollama_ok:
        print("\n⚠️  Please fix Ollama issues before continuing")
        return
    
    # Test backend
    health_ok = await test_health_check()
    if not health_ok:
        print("\n⚠️  Backend is not running. Start with: python backend/main.py")
        return
    
    # Test WebSocket
    ws_ok = await test_websocket_connection()
    
    # Test memory
    memory_ok = await test_memory_api()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Ollama: {'✅' if ollama_ok else '❌'}")
    print(f"   Backend Health: {'✅' if health_ok else '❌'}")
    print(f"   WebSocket: {'✅' if ws_ok else '❌'}")
    print(f"   Memory API: {'✅' if memory_ok else '❌'}")
    
    if all([ollama_ok, health_ok, ws_ok, memory_ok]):
        print("\n✅ All tests passed! The chatbot is ready to use.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())