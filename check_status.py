#!/usr/bin/env python3
"""
Check status of both services
"""
import requests
import time

def check_dashboard():
    try:
        response = requests.get("http://127.0.0.1:8050/", timeout=5)
        return response.status_code == 200, response.status_code
    except Exception as e:
        return False, str(e)

def check_backend():
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else response.status_code
    except Exception as e:
        return False, str(e)

def main():
    print("Checking service status...")
    print("=" * 50)
    
    # Check backend
    backend_ok, backend_info = check_backend()
    print(f"Backend (localhost:8000): {'✅ Running' if backend_ok else '❌ Not accessible'}")
    if backend_ok:
        print(f"  Status: {backend_info.get('status', 'unknown')}")
        print(f"  Ollama: {backend_info.get('components', {}).get('ollama', 'unknown')}")
    else:
        print(f"  Error: {backend_info}")
    
    print()
    
    # Check dashboard
    dashboard_ok, dashboard_info = check_dashboard()
    print(f"Dashboard (127.0.0.1:8050): {'✅ Running' if dashboard_ok else '❌ Not accessible'}")
    if not dashboard_ok:
        print(f"  Error: {dashboard_info}")
    
    print()
    print("=" * 50)
    
    if backend_ok and dashboard_ok:
        print("✅ Both services are running!")
        print(f"Dashboard URL: http://127.0.0.1:8050/")
        print(f"Try accessing in a different browser or incognito mode")
        print(f"You can also try: http://localhost:8050/")
    else:
        print("⚠️  One or more services need attention")

if __name__ == "__main__":
    main()