#!/usr/bin/env python3
"""
Test script to verify AI agent tools are working
"""
import requests
import json
import time


def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get("http://localhost:8000/api/health")
        return response.status_code == 200
    except:
        return False


def test_dashboard_state():
    """Test dashboard state API"""
    try:
        response = requests.get("http://localhost:8000/api/dashboard/state")
        if response.status_code == 200:
            data = response.json()
            print("📊 Current Dashboard State:")
            state = data.get('data', {})
            print(f"  Gen Z Adoption Rate: {state.get('gen_z_adoption_rate', 'N/A')}%")
            print(f"  Retail Spending: ${state.get('retail_spending', 'N/A'):,}")
            print(f"  Federal Readiness: {state.get('federal_readiness', 'N/A')}%")
            return True
    except Exception as e:
        print(f"❌ Dashboard state error: {e}")
        return False


def test_agent_tool_usage():
    """Test AI agent using tools"""
    test_messages = [
        "What is the current Gen Z adoption rate?",
        "Set the Gen Z adoption rate to 35%",
        "What are all the available dashboard variables?",
        "Calculate the 2025 consumer market projection",
        "Update retail spending to 600000"
    ]
    
    print("\n🤖 Testing AI Agent Tool Usage:")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n[Test {i}] You: {message}")
        
        try:
            response = requests.post(
                'http://localhost:8000/api/chat',
                json={'message': message},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get('response', 'No response')
                print(f"[Test {i}] AI: {bot_response}")
                
                # Show tool usage if any
                if 'tool_used' in data:
                    print(f"[Test {i}] 🔧 Tool Used: {data['tool_used']}")
                    tool_result = data.get('tool_result', {})
                    if tool_result.get('success'):
                        print(f"[Test {i}] ✅ Tool Result: Success")
                    else:
                        print(f"[Test {i}] ❌ Tool Result: {tool_result.get('message', 'Failed')}")
            else:
                print(f"[Test {i}] ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"[Test {i}] ❌ Error: {e}")
        
        time.sleep(2)  # Brief pause between tests


def main():
    print("Testing AI Agent Tool Functionality")
    print("=" * 50)
    
    # Test backend
    if not test_backend_health():
        print("❌ Backend not running. Please start with:")
        print("   cd agentic-commerce-chatbot && ./launch.sh")
        return
    
    print("✅ Backend is running")
    
    # Test dashboard state
    if not test_dashboard_state():
        print("❌ Dashboard state API not working")
        return
    
    print("✅ Dashboard state API working")
    
    # Test agent tools
    test_agent_tool_usage()
    
    print("\n" + "=" * 50)
    print("🎯 Tool Testing Complete!")
    print("\nThe AI agent should now be able to:")
    print("• Read dashboard variables")
    print("• Update dashboard parameters") 
    print("• Calculate market projections")
    print("• List available variables")


if __name__ == "__main__":
    main()