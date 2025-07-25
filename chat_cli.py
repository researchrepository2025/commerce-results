#!/usr/bin/env python3
"""
Command-line interface for testing AI chat
"""
import requests
import json
import sys


def chat_with_ai():
    """Simple CLI chat interface"""
    print("AI Market Assistant CLI")
    print("=" * 50)
    print("Type 'quit' to exit")
    print("Type 'help' for available commands")
    print("=" * 50)
    
    # Test backend connection
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ Connected to AI backend")
        else:
            print("❌ Backend not responding properly")
            return
    except:
        print("❌ Cannot connect to backend at http://localhost:8000")
        print("   Please start the backend first:")
        print("   cd agentic-commerce-chatbot && python backend/main_simple.py")
        return
    
    print()
    
    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("- 'list variables' - Show all dashboard variables")
                print("- 'get <variable>' - Get value of a variable")
                print("- 'set <variable> to <value>' - Update a variable")
                print("- 'calculate <segment> <year>' - Calculate projections")
                print("- 'quit' - Exit the chat\n")
                continue
            
            if not user_input:
                continue
            
            # Send to AI
            print("AI: ", end="", flush=True)
            
            response = requests.post(
                'http://localhost:8000/api/chat',
                json={'message': user_input},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', 'No response')
                print(ai_response)
                
                # Show tool usage if any
                if 'tool_used' in data:
                    print(f"\n[Tool: {data['tool_used']}]")
                    tool_result = data.get('tool_result', {})
                    if tool_result.get('success'):
                        if 'data' in tool_result:
                            # Format data nicely
                            if isinstance(tool_result['data'], dict):
                                for key, value in list(tool_result['data'].items())[:5]:
                                    print(f"  {key}: {value}")
                                if len(tool_result['data']) > 5:
                                    print(f"  ... and {len(tool_result['data']) - 5} more")
            else:
                print(f"Error: Backend returned status {response.status_code}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
        
        print()  # Blank line for readability


if __name__ == "__main__":
    chat_with_ai()