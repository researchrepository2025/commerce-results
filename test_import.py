import sys
import os

# Add AI chatbot integration
sys.path.append(os.path.join(os.path.dirname(__file__), 'agentic-commerce-chatbot'))

print("Python path:")
for p in sys.path:
    print(f"  {p}")

print("\nTrying to import...")
try:
    from frontend.dashboard_integration import integrate_ai_with_enhanced_dashboard
    print("✅ Import successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    
    # Try to diagnose
    try:
        import frontend
        print("✅ Can import frontend module")
        print(f"   Frontend location: {frontend.__file__}")
    except:
        print("❌ Cannot import frontend module")
    
    try:
        import frontend.dashboard_integration
        print("✅ Can import frontend.dashboard_integration")
    except Exception as e2:
        print(f"❌ Cannot import frontend.dashboard_integration: {e2}")