"""
Enhanced integration with full WebSocket connectivity
"""
from dash import html, dcc, Input, Output, State, callback, MATCH, ALL
import json
import uuid


def add_ai_chat_with_websocket(app, layout):
    """Add AI chat with WebSocket connectivity to dashboard"""
    
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
        }, children=[
            html.Div([
                html.Div("AI Assistant", style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': '#666'}),
                html.Div("Hello! I'm your AI assistant for the Agentic Commerce Market Analysis Dashboard. I can help you understand market projections, update parameters, and analyze trends. What would you like to explore?", 
                        style={
                            'backgroundColor': '#e9ecef',
                            'padding': '10px',
                            'borderRadius': '10px',
                            'marginRight': '50px'
                        })
            ], id={'type': 'chat-message', 'index': 0}, style={'marginBottom': '10px'})
        ]),
        
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
                },
                n_submit=0
            ),
            html.Button('Send', id='chat-send-button', 
                       n_clicks=0,
                       style={
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
    
    # Stores for WebSocket state
    websocket_store = dcc.Store(id='websocket-state', data={'connected': False, 'message_count': 0})
    pending_messages = dcc.Store(id='pending-messages', data=[])
    
    # Interval for WebSocket updates
    websocket_interval = dcc.Interval(
        id='websocket-interval',
        interval=100,  # Check every 100ms
        disabled=True
    )
    
    # Toggle chat visibility
    @app.callback(
        [Output('chat-container', 'style'),
         Output('chat-toggle-button', 'style'),
         Output('websocket-interval', 'disabled')],
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
            return container_style, button_style, True
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'chat-toggle-button':
            # Show chat
            container_style['display'] = 'flex'
            button_style['display'] = 'none'
            interval_disabled = False  # Enable WebSocket polling
        else:
            # Hide chat
            container_style['display'] = 'none'
            button_style['display'] = 'block'
            interval_disabled = True  # Disable WebSocket polling
            
        return container_style, button_style, interval_disabled
    
    # Handle message sending
    @app.callback(
        [Output('pending-messages', 'data'),
         Output('chat-input', 'value'),
         Output('chat-input', 'n_submit')],
        [Input('chat-send-button', 'n_clicks'),
         Input('chat-input', 'n_submit')],
        [State('chat-input', 'value'),
         State('pending-messages', 'data')],
        prevent_initial_call=True
    )
    def queue_message(n_clicks, n_submit, input_value, pending):
        if not input_value or not input_value.strip():
            return pending, '', 0
            
        # Add message to pending queue
        pending.append({
            'type': 'user',
            'content': input_value.strip(),
            'id': str(uuid.uuid4())
        })
        
        return pending, '', 0
    
    # WebSocket communication handler
    @app.callback(
        [Output('chat-messages', 'children'),
         Output('websocket-state', 'data'),
         Output('pending-messages', 'data', allow_duplicate=True)],
        [Input('websocket-interval', 'n_intervals')],
        [State('chat-messages', 'children'),
         State('websocket-state', 'data'),
         State('pending-messages', 'data')],
        prevent_initial_call=True
    )
    def handle_websocket_communication(n_intervals, messages, ws_state, pending):
        # This callback will be replaced by clientside callback
        # For now, just process pending messages locally
        
        if pending:
            for msg in pending:
                # Add user message
                user_msg = html.Div([
                    html.Div("You", style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': '#007bff'}),
                    html.Div(msg['content'], style={
                        'backgroundColor': '#007bff',
                        'color': 'white',
                        'padding': '10px',
                        'borderRadius': '10px',
                        'marginLeft': '50px'
                    })
                ], id={'type': 'chat-message', 'index': ws_state['message_count'] + 1}, 
                   style={'marginBottom': '10px'})
                
                messages.append(user_msg)
                ws_state['message_count'] += 1
                
                # Simulate bot response (will be replaced by WebSocket)
                bot_response = "I'm processing your request about: " + msg['content'] + ". Please ensure the backend is running at ws://localhost:8000/ws/agent for real responses."
                
                bot_msg = html.Div([
                    html.Div("AI Assistant", style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': '#666'}),
                    html.Div(bot_response, style={
                        'backgroundColor': '#e9ecef',
                        'padding': '10px',
                        'borderRadius': '10px',
                        'marginRight': '50px'
                    })
                ], id={'type': 'chat-message', 'index': ws_state['message_count'] + 2}, 
                   style={'marginBottom': '10px'})
                
                messages.append(bot_msg)
                ws_state['message_count'] += 2
            
            # Clear pending messages
            pending = []
        
        return messages, ws_state, pending
    
    # Add clientside callback for WebSocket
    app.clientside_callback(
        """
        function(n_intervals, pending, wsState, messages) {
            // Initialize WebSocket if not connected
            if (!window.aiChatWebSocket && pending.length > 0) {
                try {
                    window.aiChatWebSocket = new WebSocket('ws://localhost:8000/ws/agent');
                    
                    window.aiChatWebSocket.onopen = function() {
                        console.log('AI Chat WebSocket connected');
                        wsState.connected = true;
                    };
                    
                    window.aiChatWebSocket.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        console.log('Received from AI:', data);
                        
                        // Handle different message types
                        if (data.type === 'text') {
                            // Add AI response to messages
                            const aiMsg = {
                                type: 'ai',
                                content: data.content.text,
                                timestamp: new Date().toISOString()
                            };
                            
                            // Store in window for retrieval
                            if (!window.aiChatResponses) {
                                window.aiChatResponses = [];
                            }
                            window.aiChatResponses.push(aiMsg);
                        }
                    };
                    
                    window.aiChatWebSocket.onerror = function(error) {
                        console.error('WebSocket error:', error);
                        wsState.connected = false;
                    };
                    
                    window.aiChatWebSocket.onclose = function() {
                        console.log('WebSocket disconnected');
                        wsState.connected = false;
                        window.aiChatWebSocket = null;
                    };
                } catch (e) {
                    console.error('Failed to create WebSocket:', e);
                }
            }
            
            // Send pending messages
            if (window.aiChatWebSocket && window.aiChatWebSocket.readyState === WebSocket.OPEN && pending.length > 0) {
                pending.forEach(msg => {
                    const wsMessage = {
                        content: {
                            text: msg.content
                        }
                    };
                    window.aiChatWebSocket.send(JSON.stringify(wsMessage));
                    console.log('Sent to AI:', wsMessage);
                });
            }
            
            // Check for new AI responses
            if (window.aiChatResponses && window.aiChatResponses.length > 0) {
                // Process responses (this will be handled by the Python callback)
                const responses = window.aiChatResponses;
                window.aiChatResponses = [];
                return [messages, wsState, [], responses];
            }
            
            return [messages, wsState, wsState.connected ? [] : pending, []];
        }
        """,
        [Output('chat-messages', 'children', allow_duplicate=True),
         Output('websocket-state', 'data', allow_duplicate=True),
         Output('pending-messages', 'data', allow_duplicate=True),
         Output('websocket-interval', 'interval')],  # Dummy output to get AI responses
        [Input('websocket-interval', 'n_intervals')],
        [State('pending-messages', 'data'),
         State('websocket-state', 'data'),
         State('chat-messages', 'children')],
        prevent_initial_call=True
    )
    
    # Create wrapper with all components
    wrapped_layout = html.Div([
        layout,
        chat_button,
        chat_container,
        websocket_store,
        pending_messages,
        websocket_interval
    ])
    
    return wrapped_layout


def integrate_ai_with_enhanced_dashboard(app):
    """Factory function for compatibility"""
    class EnhancedIntegration:
        def add_chat_to_dashboard(self, layout):
            return add_ai_chat_with_websocket(app, layout)
    
    return EnhancedIntegration()