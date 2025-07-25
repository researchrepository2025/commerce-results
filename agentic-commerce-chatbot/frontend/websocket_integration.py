"""
WebSocket integration using server-side handling
"""
from dash import html, dcc, Input, Output, State, callback
import json
import uuid
import asyncio
import websockets
import threading
from queue import Queue
import time


class WebSocketClient:
    """Manages WebSocket connection to AI backend"""
    
    def __init__(self, url="ws://localhost:8000/ws/agent"):
        self.url = url
        self.ws = None
        self.loop = None
        self.thread = None
        self.incoming_messages = Queue()
        self.outgoing_messages = Queue()
        self.running = False
        
    def start(self):
        """Start WebSocket client in background thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_client)
            self.thread.daemon = True
            self.thread.start()
            
    def stop(self):
        """Stop WebSocket client"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
            
    def send_message(self, text):
        """Queue message to send"""
        self.outgoing_messages.put({
            "content": {"text": text}
        })
        
    def get_messages(self):
        """Get all received messages"""
        messages = []
        while not self.incoming_messages.empty():
            try:
                messages.append(self.incoming_messages.get_nowait())
            except:
                break
        return messages
        
    def _run_client(self):
        """Run WebSocket client in asyncio loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._client_loop())
        
    async def _client_loop(self):
        """Main WebSocket client loop"""
        while self.running:
            try:
                async with websockets.connect(self.url) as websocket:
                    self.ws = websocket
                    print("WebSocket connected to AI backend")
                    
                    # Handle incoming and outgoing messages
                    receive_task = asyncio.create_task(self._receive_messages())
                    send_task = asyncio.create_task(self._send_messages())
                    
                    await asyncio.gather(receive_task, send_task)
                    
            except Exception as e:
                print(f"WebSocket error: {e}")
                await asyncio.sleep(5)  # Retry after 5 seconds
                
    async def _receive_messages(self):
        """Receive messages from WebSocket"""
        while self.running and self.ws:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                self.incoming_messages.put(data)
            except:
                break
                
    async def _send_messages(self):
        """Send queued messages via WebSocket"""
        while self.running and self.ws:
            try:
                # Check for messages to send
                if not self.outgoing_messages.empty():
                    message = self.outgoing_messages.get()
                    await self.ws.send(json.dumps(message))
                await asyncio.sleep(0.1)
            except:
                break


# Global WebSocket client instance
ws_client = WebSocketClient()


def add_ai_chat_with_websocket(app, layout):
    """Add AI chat with WebSocket connectivity to dashboard"""
    
    # Start WebSocket client
    ws_client.start()
    
    # Create chat UI components
    chat_button = html.Button(
        "💬 AI Assistant",
        id="chat-toggle-button",
        style={
            'position': 'fixed',
            'bottom': '20px',
            'right': '20px',
            'zIndex': '9999',
            'padding': '10px 20px',
            'backgroundColor': '#007bff',
            'color': 'white',
            'border': 'none',
            'borderRadius': '25px',
            'fontSize': '16px',
            'cursor': 'pointer',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }
    )
    
    chat_container = html.Div([
        # Header
        html.Div([
            html.H4("AI Market Assistant", style={'margin': '0', 'color': 'white'}),
            html.Button("×", id="chat-close-button", style={
                'background': 'none',
                'border': 'none',
                'color': 'white',
                'fontSize': '24px',
                'cursor': 'pointer',
                'padding': '0',
                'marginLeft': 'auto'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'padding': '15px',
            'backgroundColor': '#007bff',
            'borderTopLeftRadius': '10px',
            'borderTopRightRadius': '10px'
        }),
        
        # Messages area
        html.Div(id='chat-messages', style={
            'height': '400px',
            'overflowY': 'auto',
            'padding': '15px',
            'backgroundColor': '#f8f9fa'
        }),
        
        # Status indicator
        html.Div(id='chat-status', style={
            'padding': '5px 15px',
            'backgroundColor': '#f0f0f0',
            'fontSize': '12px',
            'color': '#666'
        }),
        
        # Input area
        html.Div([
            dcc.Input(
                id='chat-input',
                type='text',
                placeholder='Type your message...',
                style={
                    'flex': '1',
                    'padding': '10px',
                    'border': '1px solid #ddd',
                    'borderRadius': '20px',
                    'marginRight': '10px',
                    'fontSize': '14px'
                }
            ),
            html.Button('Send', id='chat-send-button', style={
                'padding': '10px 20px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'borderRadius': '20px',
                'cursor': 'pointer'
            })
        ], style={
            'display': 'flex',
            'padding': '15px',
            'backgroundColor': 'white',
            'borderTop': '1px solid #ddd'
        })
    ], id='chat-container', style={
        'position': 'fixed',
        'bottom': '80px',
        'right': '20px',
        'width': '400px',
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 4px 20px rgba(0,0,0,0.15)',
        'display': 'none',
        'zIndex': '9998',
        'flexDirection': 'column'
    })
    
    # Store for messages
    messages_store = dcc.Store(id='messages-store', data=[])
    
    # Interval for checking new messages
    message_interval = dcc.Interval(
        id='message-check-interval',
        interval=500,  # Check every 500ms
        disabled=False
    )
    
    # Toggle chat visibility
    @app.callback(
        [Output('chat-container', 'style'),
         Output('chat-toggle-button', 'style')],
        [Input('chat-toggle-button', 'n_clicks'),
         Input('chat-close-button', 'n_clicks')],
        [State('chat-container', 'style'),
         State('chat-toggle-button', 'style')],
        prevent_initial_call=True
    )
    def toggle_chat(open_clicks, close_clicks, container_style, button_style):
        import dash
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return container_style, button_style
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'chat-toggle-button':
            container_style['display'] = 'flex'
            button_style['display'] = 'none'
        else:
            container_style['display'] = 'none'
            button_style['display'] = 'block'
            
        return container_style, button_style
    
    # Send message
    @app.callback(
        [Output('chat-input', 'value'),
         Output('messages-store', 'data')],
        [Input('chat-send-button', 'n_clicks'),
         Input('chat-input', 'n_submit')],
        [State('chat-input', 'value'),
         State('messages-store', 'data')],
        prevent_initial_call=True
    )
    def send_message(n_clicks, n_submit, input_value, messages):
        if not input_value or not input_value.strip():
            return '', messages
            
        # Add user message
        user_msg = {
            'type': 'user',
            'content': input_value.strip(),
            'timestamp': time.time()
        }
        messages.append(user_msg)
        
        # Send to WebSocket
        ws_client.send_message(input_value.strip())
        
        return '', messages
    
    # Check for new messages and update display
    @app.callback(
        [Output('chat-messages', 'children'),
         Output('messages-store', 'data', allow_duplicate=True),
         Output('chat-status', 'children')],
        [Input('message-check-interval', 'n_intervals')],
        [State('messages-store', 'data')],
        prevent_initial_call=True
    )
    def update_messages(n_intervals, messages):
        # Check for new messages from WebSocket
        new_messages = ws_client.get_messages()
        
        for ws_msg in new_messages:
            if ws_msg.get('type') == 'text':
                ai_msg = {
                    'type': 'ai',
                    'content': ws_msg['content']['text'],
                    'timestamp': time.time()
                }
                messages.append(ai_msg)
            elif ws_msg.get('type') == 'status':
                # Handle status messages
                pass
        
        # Build message display
        message_elements = []
        
        # Add initial greeting if no messages
        if not messages:
            message_elements.append(
                html.Div([
                    html.Div("AI Assistant", style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': '#666'}),
                    html.Div("Hello! I'm your AI assistant for the Agentic Commerce Market Analysis Dashboard. I can help you understand market projections, update parameters, and analyze trends. What would you like to explore?", 
                            style={
                                'backgroundColor': '#e9ecef',
                                'padding': '10px',
                                'borderRadius': '10px',
                                'marginRight': '50px'
                            })
                ], style={'marginBottom': '10px'})
            )
        
        # Add all messages
        for msg in messages:
            if msg['type'] == 'user':
                message_elements.append(
                    html.Div([
                        html.Div("You", style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': '#007bff'}),
                        html.Div(msg['content'], style={
                            'backgroundColor': '#007bff',
                            'color': 'white',
                            'padding': '10px',
                            'borderRadius': '10px',
                            'marginLeft': '50px'
                        })
                    ], style={'marginBottom': '10px'})
                )
            else:
                message_elements.append(
                    html.Div([
                        html.Div("AI Assistant", style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': '#666'}),
                        html.Div(msg['content'], style={
                            'backgroundColor': '#e9ecef',
                            'padding': '10px',
                            'borderRadius': '10px',
                            'marginRight': '50px'
                        })
                    ], style={'marginBottom': '10px'})
                )
        
        # Status
        status = "Connected" if ws_client.ws and ws_client.running else "Connecting..."
        
        return message_elements, messages, f"Status: {status}"
    
    # Create wrapper with all components
    wrapped_layout = html.Div([
        layout,
        chat_button,
        chat_container,
        messages_store,
        message_interval
    ])
    
    return wrapped_layout


def integrate_ai_with_enhanced_dashboard(app):
    """Factory function for compatibility"""
    class WebSocketIntegration:
        def add_chat_to_dashboard(self, layout):
            return add_ai_chat_with_websocket(app, layout)
    
    return WebSocketIntegration()