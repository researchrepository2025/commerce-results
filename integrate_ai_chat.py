"""
Integration snippet to add AI chat to dashboard_enhanced.py

Add this code to your dashboard_enhanced.py file to integrate the AI chatbot.
"""

# ============================================================================
# ADD THESE IMPORTS AT THE TOP OF dashboard_enhanced.py
# ============================================================================

import sys
import os

# Add chatbot to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agentic-commerce-chatbot'))

try:
    from frontend.dashboard_integration import integrate_ai_with_enhanced_dashboard
    AI_CHAT_AVAILABLE = True
except ImportError:
    print("AI Chat not available - please run setup.sh in agentic-commerce-chatbot/")
    AI_CHAT_AVAILABLE = False


# ============================================================================
# ADD THIS FUNCTION AFTER YOUR LAYOUT DEFINITION
# ============================================================================

def add_ai_chat_to_app(app, layout):
    """Add AI chat integration to the dashboard"""
    if not AI_CHAT_AVAILABLE:
        return layout
    
    try:
        # Create AI integration
        ai_integration = integrate_ai_with_enhanced_dashboard(app)
        
        # Wrap layout with AI components
        enhanced_layout = ai_integration.add_chat_to_dashboard(layout)
        
        print("✅ AI Chat integrated successfully!")
        print("   - Look for the 'AI Assistant' button in the bottom-right corner")
        print("   - Make sure the backend is running: python agentic-commerce-chatbot/backend/main.py")
        
        return enhanced_layout
        
    except Exception as e:
        print(f"⚠️  Could not integrate AI chat: {e}")
        return layout


# ============================================================================
# MODIFY YOUR APP INITIALIZATION (around line where app.layout is set)
# ============================================================================

# Replace this:
# app.layout = html.Div([...your layout...])

# With this:
# original_layout = html.Div([...your layout...])
# app.layout = add_ai_chat_to_app(app, original_layout)


# ============================================================================
# EXAMPLE COMPLETE INTEGRATION
# ============================================================================

"""
# Example of how the end of dashboard_enhanced.py should look:

# Create your original layout
original_layout = html.Div([
    # ... all your existing dashboard components ...
])

# Add AI chat if available
app.layout = add_ai_chat_to_app(app, original_layout)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
"""