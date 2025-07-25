#!/usr/bin/env python3
"""
Test full integration of AI chatbot with dashboard
"""
import requests
import json


def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is running")
            print(f"   - Status: {data['status']}")
            print(f"   - Ollama: {data['components']['ollama']}")
            print(f"   - Models: {data.get('models', [])}")
            return True
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False


def test_dashboard():
    """Test if dashboard is running"""
    try:
        response = requests.get("http://localhost:8050/")
        if response.status_code == 200:
            print("✅ Dashboard is running at http://localhost:8050/")
            return True
    except Exception as e:
        print(f"❌ Dashboard not accessible: {e}")
        return False


def main():
    print("Testing Agentic Commerce AI Integration")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_backend_health()
    
    print()
    
    # Test dashboard
    dashboard_ok = test_dashboard()
    
    print()
    print("=" * 50)
    
    if backend_ok and dashboard_ok:
        print("✅ All systems operational!")
        print("\nTo use the AI Assistant:")
        print("1. Open http://localhost:8050/ in your browser")
        print("2. Click the '💬 AI Assistant' button in the bottom-right")
        print("3. Start chatting about market projections!")
        print("\nExample questions:")
        print("- What is the current consumer adoption rate?")
        print("- Analyze the business segment for me")
        print("- Show me government spending projections")
        print("- Update Gen Z adoption rate to 35%")
    else:
        print("⚠️  Some components are not running")
        if not backend_ok:
            print("\nTo start the backend:")
            print("cd agentic-commerce-chatbot && ./launch.sh")
        if not dashboard_ok:
            print("\nTo start the dashboard:")
            print("python dashboard_enhanced.py")


if __name__ == "__main__":
    main()