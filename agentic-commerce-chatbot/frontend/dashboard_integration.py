"""
Integration module to add AI chat to existing Dash dashboard
"""
import json
from typing import Dict, Any, Callable
from dash import Input, Output, State, callback, html, dcc
import dash_bootstrap_components as dbc

from .chat_sidebar import AGUIClient, create_chat_sidebar, register_callbacks


class DashboardAIIntegration:
    """Integrate AI chat with existing dashboard"""
    
    def __init__(self, app, ws_url: str = "ws://localhost:8000/ws/agent"):
        self.app = app
        self.ag_ui_client = AGUIClient(ws_url)
        self.ui_update_handlers: Dict[str, Callable] = {}
        
        # Set up AG-UI client callbacks
        self.ag_ui_client.on_ui_update_callback = self.handle_ui_update
        
    def handle_ui_update(self, update: Dict[str, Any]):
        """Handle UI updates from agent"""
        component = update.get("component", "")
        action = update.get("action", "")
        data = update.get("data", {})
        
        # Call registered handler for this component
        if component in self.ui_update_handlers:
            self.ui_update_handlers[component](action, data)
        
        # Store update for processing
        # This would typically update a dcc.Store that triggers dashboard updates
        print(f"UI Update: {component} - {action} - {data}")
    
    def register_ui_handler(self, component: str, handler: Callable):
        """Register a handler for UI updates to a specific component"""
        self.ui_update_handlers[component] = handler
    
    def add_chat_to_dashboard(self, dashboard_layout):
        """Add chat components to existing dashboard layout"""
        
        # Create chat sidebar
        chat_sidebar = create_chat_sidebar(self.ag_ui_client)
        
        # Create floating action button to open chat
        chat_button = html.Div([
            dbc.Button(
                [
                    html.I(className="fas fa-comments me-2"),
                    "AI Assistant"
                ],
                id="open-chat-button",
                color="primary",
                className="shadow",
                style={
                    "position": "fixed",
                    "bottom": "20px",
                    "right": "20px",
                    "zIndex": 1000,
                    "borderRadius": "50px",
                    "padding": "12px 24px"
                }
            )
        ])
        
        # Create store for UI updates
        ui_update_store = dcc.Store(id="ui-update-store", data={})
        
        # Wrap existing layout and add chat components
        enhanced_layout = html.Div([
            dashboard_layout,
            chat_sidebar,
            chat_button,
            ui_update_store
        ])
        
        # Register chat callbacks
        register_callbacks(self.app, self.ag_ui_client)
        
        # Register UI update processor
        self._register_ui_update_processor()
        
        return enhanced_layout
    
    def _register_ui_update_processor(self):
        """Register callback to process UI updates"""
        
        @self.app.callback(
            Output("ui-update-store", "data"),
            Input("message-poller", "n_intervals"),
            State("ui-update-store", "data"),
            prevent_initial_call=True
        )
        def process_ui_updates(n_intervals, current_data):
            # This is a placeholder - in production, this would
            # actually process the UI updates and trigger dashboard changes
            return current_data


def create_update_handlers(app):
    """Create handlers for different dashboard components"""
    
    handlers = {}
    
    def consumer_projection_handler(action: str, data: Dict[str, Any]):
        """Handle updates to consumer projection"""
        # This would trigger a callback to update the consumer projection chart
        print(f"Updating consumer projection: {action} - {data}")
        
        # Example: Update a specific input value
        # This would need to be connected to actual dashboard components
        @app.callback(
            Output("projection-data", "data", allow_duplicate=True),
            Input("ui-update-store", "data"),
            prevent_initial_call=True
        )
        def update_projection(ui_data):
            if ui_data.get("component") == "consumer-projection":
                # Process the update
                return ui_data.get("data", {})
            return dash.no_update
    
    def business_projection_handler(action: str, data: Dict[str, Any]):
        """Handle updates to business projection"""
        print(f"Updating business projection: {action} - {data}")
    
    def government_projection_handler(action: str, data: Dict[str, Any]):
        """Handle updates to government projection"""
        print(f"Updating government projection: {action} - {data}")
    
    def analysis_panel_handler(action: str, data: Dict[str, Any]):
        """Handle updates to analysis panel"""
        print(f"Updating analysis panel: {action} - {data}")
    
    handlers["consumer-projection"] = consumer_projection_handler
    handlers["business-projection"] = business_projection_handler
    handlers["government-projection"] = government_projection_handler
    handlers["analysis-panel"] = analysis_panel_handler
    
    return handlers


def integrate_ai_with_enhanced_dashboard(app):
    """
    Integrate AI chat with the enhanced dashboard.
    This function should be called in the dashboard_enhanced.py file.
    """
    
    # Create integration
    ai_integration = DashboardAIIntegration(app)
    
    # Create and register handlers
    handlers = create_update_handlers(app)
    for component, handler in handlers.items():
        ai_integration.register_ui_handler(component, handler)
    
    # Add specific callbacks for dashboard updates
    @app.callback(
        [Output({'type': 'adoption-2025', 'generation': 'Gen Z'}, 'value', allow_duplicate=True),
         Output({'type': 'adoption-2025', 'generation': 'Millennials'}, 'value', allow_duplicate=True),
         Output({'type': 'adoption-2025', 'generation': 'Gen X'}, 'value', allow_duplicate=True),
         Output({'type': 'adoption-2025', 'generation': 'Baby Boomers'}, 'value', allow_duplicate=True)],
        Input("ui-update-store", "data"),
        prevent_initial_call=True
    )
    def update_consumer_adoptions(ui_data):
        """Update consumer adoption rates from AI commands"""
        if not ui_data or ui_data.get("component") != "consumer-projection":
            return [dash.no_update] * 4
        
        data = ui_data.get("data", {})
        if data.get("parameter") == "adoption_rate" and data.get("segment") == "consumer":
            # Parse which generation to update
            generation = data.get("generation", "all")
            value = data.get("value", 0) * 100  # Convert to percentage
            
            # Return updates for each generation
            if generation == "Gen Z":
                return [value, dash.no_update, dash.no_update, dash.no_update]
            elif generation == "Millennials":
                return [dash.no_update, value, dash.no_update, dash.no_update]
            elif generation == "Gen X":
                return [dash.no_update, dash.no_update, value, dash.no_update]
            elif generation == "Baby Boomers":
                return [dash.no_update, dash.no_update, dash.no_update, value]
            elif generation == "all":
                # Update all generations
                return [value, value, value, value]
        
        return [dash.no_update] * 4
    
    @app.callback(
        Output("update-button", "n_clicks", allow_duplicate=True),
        Input("ui-update-store", "data"),
        State("update-button", "n_clicks"),
        prevent_initial_call=True
    )
    def trigger_projection_update(ui_data, current_clicks):
        """Trigger projection recalculation after AI updates"""
        if ui_data and any(key in ui_data.get("component", "") for key in ["projection", "update"]):
            # Increment click count to trigger update
            return (current_clicks or 0) + 1
        return dash.no_update
    
    return ai_integration


# Example integration code to add to dashboard_enhanced.py:
"""
# At the top of dashboard_enhanced.py, add:
from agentic_commerce_chatbot.frontend.dashboard_integration import integrate_ai_with_enhanced_dashboard

# After creating the app and layout, add:
ai_integration = integrate_ai_with_enhanced_dashboard(app)

# Modify the layout creation to include AI components:
original_layout = app.layout  # Save original layout
app.layout = ai_integration.add_chat_to_dashboard(original_layout)
"""