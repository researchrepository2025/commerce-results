#!/usr/bin/env python3
"""
Simple test client for the AI chatbot
"""
import asyncio
import json
import websockets


async def test_chat():
    """Test the WebSocket chat connection"""
    uri = "ws://localhost:8000/ws/agent"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to AI agent!")
            
            # Receive welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"\nAI: {welcome_data['content']['text']}")
            
            # Test messages
            test_messages = [
                "Hello! Can you help me understand the agentic commerce market?",
                "What's the current consumer adoption rate?",
                "Can you analyze the business segment for me?"
            ]
            
            for message in test_messages:
                print(f"\nYou: {message}")
                
                # Send message
                await websocket.send(json.dumps({
                    "content": {"text": message}
                }))
                
                # Receive status
                status = await websocket.recv()
                status_data = json.loads(status)
                if status_data['type'] == 'status':
                    print(f"Status: {status_data['content']['text']}")
                
                # Receive response
                response = await websocket.recv()
                response_data = json.loads(response)
                print(f"AI: {response_data['content']['text']}")
                
                # Check for UI updates
                try:
                    # Wait briefly for any UI updates
                    ui_update = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    ui_data = json.loads(ui_update)
                    if ui_data['type'] == 'ui_update':
                        print(f"UI Update: {ui_data['content']}")
                except asyncio.TimeoutError:
                    pass  # No UI update, that's fine
                
                await asyncio.sleep(1)  # Brief pause between messages
                
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure the backend server is running:")
        print("python backend/main_simple.py")


if __name__ == "__main__":
    print("Testing AI Chatbot WebSocket Connection...")
    print("=" * 50)
    asyncio.run(test_chat())