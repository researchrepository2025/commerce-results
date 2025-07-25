"""
Dash chat sidebar component with AG-UI client integration
"""
import json
import asyncio
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import uuid

import dash
from dash import html, dcc, Input, Output, State, callback, ALL, MATCH
import dash_bootstrap_components as dbc
import websocket
from queue import Queue


class AGUIClient:
    """AG-UI WebSocket client for Dash"""
    
    def __init__(self, ws_url: str = "ws://localhost:8000/ws/agent"):
        self.ws_url = ws_url
        self.ws = None
        self.message_queue = Queue()
        self.is_connected = False
        self.on_message_callback: Optional[Callable] = None
        self.on_ui_update_callback: Optional[Callable] = None
        self.session_id = str(uuid.uuid4())
        
    def connect(self):
        """Connect to WebSocket server"""
        def on_message(ws, message):
            try:
                msg = json.loads(message)
                self.message_queue.put(msg)
                
                # Handle different message types
                if msg.get("type") == "ui_update" and self.on_ui_update_callback:
                    self.on_ui_update_callback(msg.get("content", {}))
                elif self.on_message_callback:
                    self.on_message_callback(msg)
                    
            except Exception as e:
                print(f"Error processing message: {e}")
        
        def on_error(ws, error):
            print(f"WebSocket error: {error}")
            self.is_connected = False
        
        def on_close(ws, close_status_code, close_msg):
            print(f"WebSocket closed: {close_msg}")
            self.is_connected = False
        
        def on_open(ws):
            print("WebSocket connected")
            self.is_connected = True
        
        # Create WebSocket connection
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # Run in separate thread
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        # Wait for connection
        import time
        for _ in range(10):
            if self.is_connected:
                break
            time.sleep(0.5)
    
    def send_message(self, text: str):
        """Send message to agent"""
        if self.ws and self.is_connected:
            message = {
                "type": "text",
                "content": {"text": text},
                "metadata": {"session_id": self.session_id}
            }
            self.ws.send(json.dumps(message))
    
    def close(self):
        """Close WebSocket connection"""
        if self.ws:
            self.ws.close()


def create_chat_sidebar(ag_ui_client: AGUIClient):
    """Create the chat sidebar component"""
    
    return dbc.Offcanvas(
        [
            # Header
            dbc.Row([
                dbc.Col([
                    html.H4("AI Market Assistant", className="text-primary mb-0"),
                    html.Small("Powered by Local LLM", className="text-muted")
                ], width=9),
                dbc.Col([
                    dbc.Badge(
                        "Connected",
                        id="connection-status",
                        color="success",
                        pill=True,
                        className="mt-2"
                    )
                ], width=3, className="text-end")
            ], className="mb-3"),
            
            html.Hr(),
            
            # Chat messages area
            html.Div(
                id="chat-messages",
                style={
                    "height": "calc(100vh - 300px)",
                    "overflowY": "auto",
                    "backgroundColor": "#f8f9fa",
                    "borderRadius": "8px",
                    "padding": "15px",
                    "marginBottom": "15px"
                },
                children=[]
            ),
            
            # Suggestions
            html.Div(
                id="suggestions-area",
                className="mb-3",
                children=[]
            ),
            
            # Input area
            dbc.InputGroup([
                dbc.Textarea(
                    id="chat-input",
                    placeholder="Ask about market projections...",
                    rows=2,
                    style={"resize": "none"}
                ),
                dbc.Button(
                    html.I(className="fas fa-paper-plane"),
                    id="send-button",
                    color="primary",
                    className="align-self-end",
                    n_clicks=0
                )
            ]),
            
            # Typing indicator
            html.Div(
                id="typing-indicator",
                className="text-muted small mt-2",
                style={"display": "none"},
                children=[
                    html.I(className="fas fa-circle-notch fa-spin me-2"),
                    "AI is thinking..."
                ]
            ),
            
            # Hidden stores
            dcc.Store(id="chat-history", data=[]),
            dcc.Store(id="pending-ui-updates", data=[]),
            dcc.Interval(id="message-poller", interval=100, n_intervals=0)
        ],
        id="chat-sidebar",
        title="",  # Empty title since we have custom header
        placement="end",
        is_open=False,
        style={"width": "450px"},
        backdrop=False
    )


def create_message_component(message: Dict[str, Any]) -> html.Div:
    """Create a message component based on message type and role"""
    
    content = message.get("content", {})
    msg_type = message.get("type", "text")
    
    if msg_type == "text":
        text = content.get("text", "")
        role = content.get("role", message.get("metadata", {}).get("role", "assistant"))
        
        if role == "user":
            return html.Div([
                html.Div([
                    html.Small("You", className="text-muted d-block mb-1"),
                    html.Div(
                        text,
                        className="bg-primary text-white p-3 rounded",
                        style={"marginLeft": "50px"}
                    )
                ], className="mb-3")
            ])
        else:
            # Assistant message
            return html.Div([
                html.Div([
                    html.Small("AI Assistant", className="text-muted d-block mb-1"),
                    html.Div(
                        dcc.Markdown(text),
                        className="bg-white p-3 rounded shadow-sm",
                        style={"marginRight": "50px"}
                    )
                ], className="mb-3")
            ])
    
    elif msg_type == "status":
        status = content.get("status", "")
        text = content.get("text", "")
        
        color_map = {
            "thinking": "info",
            "success": "success",
            "error": "danger"
        }
        
        return dbc.Alert(
            [
                html.I(className="fas fa-info-circle me-2"),
                text
            ],
            color=color_map.get(status, "secondary"),
            className="mb-2",
            dismissable=True
        )
    
    elif msg_type == "error":
        error_text = content.get("message", content.get("error", "Unknown error"))
        return dbc.Alert(
            [
                html.I(className="fas fa-exclamation-triangle me-2"),
                error_text
            ],
            color="danger",
            className="mb-2"
        )
    
    return html.Div()


def create_suggestion_buttons(suggestions: List[str]) -> List[dbc.Button]:
    """Create suggestion buttons"""
    buttons = []
    for i, suggestion in enumerate(suggestions[:4]):  # Limit to 4 suggestions
        buttons.append(
            dbc.Button(
                suggestion,
                id={"type": "suggestion-btn", "index": i},
                color="outline-secondary",
                size="sm",
                className="me-2 mb-2",
                n_clicks=0
            )
        )
    return buttons


# Callback to toggle sidebar
def register_callbacks(app, ag_ui_client: AGUIClient):
    """Register all callbacks for the chat sidebar"""
    
    @app.callback(
        Output("chat-sidebar", "is_open"),
        Input("open-chat-button", "n_clicks"),  # Assuming this button exists in main dashboard
        State("chat-sidebar", "is_open"),
        prevent_initial_call=True
    )
    def toggle_sidebar(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
    
    
    @app.callback(
        [Output("chat-messages", "children"),
         Output("suggestions-area", "children"),
         Output("typing-indicator", "style"),
         Output("connection-status", "children"),
         Output("connection-status", "color")],
        [Input("message-poller", "n_intervals"),
         Input("send-button", "n_clicks"),
         Input({"type": "suggestion-btn", "index": ALL}, "n_clicks")],
        [State("chat-input", "value"),
         State("chat-history", "data"),
         State("chat-messages", "children")],
        prevent_initial_call=False
    )
    def update_chat(n_intervals, send_clicks, suggestion_clicks, 
                   input_value, chat_history, current_messages):
        
        # Initialize if needed
        if not ag_ui_client.is_connected:
            ag_ui_client.connect()
        
        # Check connection status
        connection_status = "Connected" if ag_ui_client.is_connected else "Disconnected"
        connection_color = "success" if ag_ui_client.is_connected else "danger"
        
        # Handle sending messages
        ctx = dash.callback_context
        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"]
            
            # Send user message
            if "send-button" in trigger_id and input_value:
                ag_ui_client.send_message(input_value)
                
                # Add user message to display
                user_msg = {
                    "type": "text",
                    "content": {"text": input_value, "role": "user"}
                }
                current_messages.append(create_message_component(user_msg))
                
                # Clear input
                dash.callback_context.outputs_list[0].clear()
            
            # Handle suggestion clicks
            elif "suggestion-btn" in trigger_id:
                # Find which suggestion was clicked
                for i, n_clicks in enumerate(suggestion_clicks):
                    if n_clicks and n_clicks > 0:
                        # Get suggestion text from current suggestions
                        suggestions_div = current_messages[-1] if current_messages else None
                        if suggestions_div and hasattr(suggestions_div, 'children'):
                            # Extract suggestion text and send
                            # This is simplified - in production, store suggestions properly
                            ag_ui_client.send_message(f"Suggestion {i}")
        
        # Process queued messages
        new_messages = []
        suggestions = []
        show_typing = False
        
        while not ag_ui_client.message_queue.empty():
            msg = ag_ui_client.message_queue.get()
            
            # Handle different message types
            if msg.get("type") == "text":
                new_messages.append(create_message_component(msg))
                
                # Extract suggestions if present
                content = msg.get("content", {})
                if "suggestions" in content:
                    suggestions = content["suggestions"]
            
            elif msg.get("type") == "status":
                if msg.get("content", {}).get("status") == "thinking":
                    show_typing = True
                else:
                    show_typing = False
                new_messages.append(create_message_component(msg))
            
            elif msg.get("type") == "error":
                new_messages.append(create_message_component(msg))
                show_typing = False
        
        # Update messages
        if new_messages:
            current_messages.extend(new_messages)
        
        # Create suggestion buttons
        suggestion_components = []
        if suggestions:
            suggestion_components = [
                html.Div([
                    html.Small("Suggestions:", className="text-muted d-block mb-2"),
                    html.Div(create_suggestion_buttons(suggestions))
                ])
            ]
        
        # Typing indicator style
        typing_style = {"display": "block"} if show_typing else {"display": "none"}
        
        return (
            current_messages,
            suggestion_components,
            typing_style,
            connection_status,
            connection_color
        )
    
    
    @app.callback(
        Output("chat-input", "value"),
        Input("send-button", "n_clicks"),
        prevent_initial_call=True
    )
    def clear_input(n_clicks):
        return ""
    
    
    # Handle Enter key in textarea
    app.clientside_callback(
        """
        function(value) {
            if (value && value.includes('\\n')) {
                // Trigger send button click
                document.getElementById('send-button').click();
                return value.replace('\\n', '');
            }
            return value;
        }
        """,
        Output("chat-input", "value", allow_duplicate=True),
        Input("chat-input", "value"),
        prevent_initial_call=True
    )